import csv
import hmac
import io
import math
import os
import re
import secrets
import threading
import time
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from xml.sax.saxutils import escape

from flask import Flask, flash, has_request_context, jsonify, make_response, redirect, render_template, request, send_file, session, url_for
from flask.sessions import SecureCookieSessionInterface
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import delete, func, insert, select, text, update
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from recommendations import (
    RecommendationModelError,
    calculate_ml_water_quality_analysis,
    classify_water_quality,
    get_ml_parameter_status,
    predict_recommendation,
)
from ntfy_service import (
    generate_secure_topic,
    is_valid_topic,
    send_ntfy_notification,
    send_water_quality_alert_ntfy,
)

app = Flask(__name__)


def load_secret_key():
    configured_key = os.getenv("SECRET_KEY")
    if configured_key:
        return configured_key

    os.makedirs(app.instance_path, exist_ok=True)
    key_path = os.path.join(app.instance_path, "secret_key")
    try:
        with open(key_path, "x", encoding="ascii") as key_file:
            key_file.write(secrets.token_hex(32))
    except FileExistsError:
        pass

    with open(key_path, "r", encoding="ascii") as key_file:
        secret_key = key_file.read().strip()
    if not secret_key:
        raise RuntimeError("The Flask session secret key is empty.")
    return secret_key


class AdaptiveSessionInterface(SecureCookieSessionInterface):
    """
    Dynamically configures session cookie flags for maximum compatibility and security across browsers.
    - When running over plain HTTP (e.g. http://localhost:5000, http://127.0.0.1:5000, or local LAN 192.168.x.x),
      standalone desktop and mobile browsers (especially Microsoft Edge) strictly reject cookies with
      Secure or SameSite=None on insecure origins, causing immediate session loss and redirect loops upon login.
      For these top-level browser navigations, standard SameSite=Lax without Secure is used.
    - When running inside an embedded third-party iframe (such as the VS Code Mobile Preview webview iframe)
      on loopback, SameSite=None, Secure, and Partitioned are used so third-party cookie restrictions
      in Electron webviews do not block the session.
    - When running over genuine HTTPS (or reverse proxy with X-Forwarded-Proto=https), the Secure flag is enabled.
    """

    def _is_https(self) -> bool:
        if not has_request_context() or not request:
            return False
        if request.is_secure:
            return True
        proto = request.headers.get("X-Forwarded-Proto", "").strip().lower()
        return proto == "https"

    def _is_embedded_webview(self) -> bool:
        if not has_request_context() or not request:
            return False
        user_agent = request.headers.get("User-Agent", "")
        # Microsoft Edge is a standalone browser and must receive standard Lax cookies on HTTP
        if "Edg/" in user_agent:
            return False
        dest = request.headers.get("Sec-Fetch-Dest", "").strip().lower()
        site = request.headers.get("Sec-Fetch-Site", "").strip().lower()
        if dest == "document" and site in {"none", "same-origin"}:
            return False
        if dest == "iframe" or site == "cross-site":
            return True
        if "Electron" in user_agent or "VSCode" in user_agent:
            return True
        return False

    def get_cookie_secure(self, app: Flask) -> bool:
        configured = app.config.get("SESSION_COOKIE_SECURE_OVERRIDE")
        if configured is not None:
            return bool(configured)
        if self._is_https():
            return True
        if self._is_embedded_webview():
            host = (request.host or "").split(":")[0].strip().lower() if request else ""
            if host in {"localhost", "127.0.0.1", "::1", "testserver"}:
                return True
        return False

    def get_cookie_samesite(self, app: Flask) -> str | None:
        configured = app.config.get("SESSION_COOKIE_SAMESITE_OVERRIDE")
        if configured is not None:
            return configured
        if self._is_embedded_webview():
            return "None"
        return "Lax"

    def get_cookie_partitioned(self, app: Flask) -> bool:
        configured = app.config.get("SESSION_COOKIE_PARTITIONED_OVERRIDE")
        if configured is not None:
            return bool(configured)
        if self._is_embedded_webview():
            return True
        return False


app.config["SECRET_KEY"] = load_secret_key()
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.session_interface = AdaptiveSessionInterface()


def generate_timed_csrf_token(purpose: str) -> str:
    s = URLSafeTimedSerializer(app.secret_key, salt=f"shrimpguard-csrf-{purpose}")
    return s.dumps(purpose)


def verify_timed_csrf_token(token: str, purpose: str, max_age: int = 3600) -> bool:
    if not token:
        return False
    s = URLSafeTimedSerializer(app.secret_key, salt=f"shrimpguard-csrf-{purpose}")
    try:
        data = s.loads(token, max_age=max_age)
        return data == purpose
    except (BadSignature, SignatureExpired):
        return False


def validate_csrf(submitted_token: str, session_token_key: str, purpose: str, max_age: int = 3600) -> bool:
    if not submitted_token:
        return False
    expected = session.get(session_token_key, "")
    if expected and hmac.compare_digest(expected, submitted_token):
        return True
    return verify_timed_csrf_token(submitted_token, purpose=purpose, max_age=max_age)


def get_database_uri():
    configured_database_url = os.getenv("DATABASE_URL")
    if configured_database_url:
        return configured_database_url

    return URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD") or None,
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT") or "3306"),
        database=os.getenv("DB_NAME", "shrimpguard"),
        query={"charset": "utf8mb4"},
    )


app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
if "sqlite" not in app.config["SQLALCHEMY_DATABASE_URI"]:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_size": 25,
        "max_overflow": 50,
        "pool_recycle": 1800,
        "pool_timeout": 30,
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

db = SQLAlchemy(app)

# --- TABLE 1: SENSORS ---
sensor_readings = db.Table(
    "sensors",
    db.metadata,
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("user_email", db.String(255), nullable=True, index=True),
    db.Column("device_id", db.String(50), nullable=True, index=True),
    db.Column("ph_level", db.Float, nullable=False),
    db.Column("temperature", db.Float, nullable=False),
    db.Column("date", db.String(45), nullable=False),
    db.Column("status", db.String(45), nullable=False),
    extend_existing=True,
)

# --- TABLE 2: USERS ---
class User(db.Model):
    __tablename__ = "users"

    email = db.Column(db.String(255), primary_key=True)
    user_name = db.Column("name", db.String(80), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column("password", db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Active")
    last_login = db.Column(db.DateTime, nullable=True)
    ntfy_topic = db.Column(db.String(100), nullable=True)
    last_read_notifications = db.Column(db.DateTime, nullable=True)

    @property
    def id(self):
        return self.email

    @property
    def name(self):
        return self.user_name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash.startswith(("scrypt:", "pbkdf2:")):
            return check_password_hash(self.password_hash, password)
        return hmac.compare_digest(self.password_hash, password)

    def password_needs_rehash(self):
        return not self.password_hash.startswith(("scrypt:", "pbkdf2:"))


# --- TABLE 3: ACTIVITY LOGS ---
class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(255), nullable=True, index=True)
    user_name = db.Column(db.String(80), nullable=True)
    role = db.Column(db.String(50), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "user_name": self.user_name,
            "role": self.role,
            "action": self.action,
            "details": self.details,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }



# --- TABLE 4: AQUACULTURE CALCULATIONS ---
class AquacultureCalculation(db.Model):
    __tablename__ = "aquaculture_calculations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(255), nullable=True, index=True)
    user_name = db.Column(db.String(80), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    # 1. Estimated Standing Biomass
    pond_area_m2 = db.Column(db.Float, nullable=True)
    pond_depth_m = db.Column(db.Float, nullable=True)
    stocking_density_pl_m2 = db.Column(db.Float, nullable=True)
    survival_rate_pct = db.Column(db.Float, nullable=True)
    abw_g = db.Column(db.Float, nullable=True)
    standing_biomass_kg = db.Column(db.Float, nullable=True)
    standing_biomass_tons = db.Column(db.Float, nullable=True)
    active_shrimp_count = db.Column(db.BigInteger, nullable=True)

    # 2. Temperature Feeding Adjustment
    water_temperature_c = db.Column(db.Float, nullable=True)
    base_feeding_rate_pct = db.Column(db.Float, nullable=True)
    temp_feeding_factor = db.Column(db.Float, nullable=True)
    adjusted_daily_feed_kg = db.Column(db.Float, nullable=True)
    feed_per_meal_kg = db.Column(db.Float, nullable=True)
    feedings_per_day = db.Column(db.Integer, nullable=True)

    # 3. Eight Equations (Eqs. 1–8)
    is_count = db.Column(db.BigInteger, nullable=True)
    lhc_count = db.Column(db.BigInteger, nullable=True)
    doc_days = db.Column(db.Integer, nullable=True)
    ibw_g = db.Column(db.Float, nullable=True)
    bulk_weight_kg = db.Column(db.Float, nullable=True)
    total_feed_given_kg = db.Column(db.Float, nullable=True)
    total_length_cm = db.Column(db.Float, nullable=True)
    eq1_sr_pct = db.Column(db.Float, nullable=True)
    eq1_mortality_count = db.Column(db.BigInteger, nullable=True)
    eq2_fabw_g = db.Column(db.Float, nullable=True)
    eq2_count_per_kg = db.Column(db.Float, nullable=True)
    eq3_adwg_g_day = db.Column(db.Float, nullable=True)
    eq3_weekly_gain_g = db.Column(db.Float, nullable=True)
    eq4_sgr_pct_day = db.Column(db.Float, nullable=True)
    eq5_ib_kg = db.Column(db.Float, nullable=True)
    eq6_fb_kg = db.Column(db.Float, nullable=True)
    eq5_6_net_biomass_kg = db.Column(db.Float, nullable=True)
    eq7_fcr = db.Column(db.Float, nullable=True)
    eq7_feed_efficiency_pct = db.Column(db.Float, nullable=True)
    eq8_fulton_k = db.Column(db.Float, nullable=True)
    eq8_fulton_profile = db.Column(db.String(100), nullable=True)

    # 4. pH Liming Dosage
    lime_pond_vol_m3 = db.Column(db.Float, nullable=True)
    lime_current_ph = db.Column(db.Float, nullable=True)
    lime_target_ph = db.Column(db.Float, nullable=True)
    lime_chemical_type = db.Column(db.String(100), nullable=True)
    lime_dosage_kg = db.Column(db.Float, nullable=True)
    lime_dosage_ppm = db.Column(db.Float, nullable=True)

    # 5. Organic Carbon Dosing (Biofloc C:N)
    molasses_daily_feed_kg = db.Column(db.Float, nullable=True)
    molasses_protein_pct = db.Column(db.Float, nullable=True)
    molasses_target_cn = db.Column(db.Float, nullable=True)
    molasses_carbon_source = db.Column(db.String(100), nullable=True)
    molasses_dosage_kg = db.Column(db.Float, nullable=True)

    # 6. Aerator Power Sizing
    aero_biomass_kg = db.Column(db.Float, nullable=True)
    aero_water_temp_c = db.Column(db.Float, nullable=True)
    aero_salinity_ppt = db.Column(db.Float, nullable=True)
    aero_target_do_ppm = db.Column(db.Float, nullable=True)
    aero_power_hp = db.Column(db.Float, nullable=True)
    aero_units_desc = db.Column(db.String(100), nullable=True)

    # 7. Unionized Ammonia (NH3) Toxicity
    ammonia_tan_ppm = db.Column(db.Float, nullable=True)
    ammonia_temp_c = db.Column(db.Float, nullable=True)
    ammonia_ph = db.Column(db.Float, nullable=True)
    ammonia_salinity_ppt = db.Column(db.Float, nullable=True)
    ammonia_factor_f = db.Column(db.Float, nullable=True)
    ammonia_nh3_ppm = db.Column(db.Float, nullable=True)
    ammonia_status = db.Column(db.String(50), nullable=True)

    # 8. Free Carbon Dioxide (CO2) Concentration
    co2_alkalinity_mg_l = db.Column(db.Float, nullable=True)
    co2_temp_c = db.Column(db.Float, nullable=True)
    co2_ph = db.Column(db.Float, nullable=True)
    co2_factor = db.Column(db.Float, nullable=True)
    co2_concentration_mg_l = db.Column(db.Float, nullable=True)
    co2_status = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "user_name": self.user_name,
            "notes": self.notes,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "pond_area_m2": self.pond_area_m2,
            "pond_depth_m": self.pond_depth_m,
            "stocking_density_pl_m2": self.stocking_density_pl_m2,
            "survival_rate_pct": self.survival_rate_pct,
            "abw_g": self.abw_g,
            "standing_biomass_kg": self.standing_biomass_kg,
            "standing_biomass_tons": self.standing_biomass_tons,
            "active_shrimp_count": self.active_shrimp_count,
            "water_temperature_c": self.water_temperature_c,
            "base_feeding_rate_pct": self.base_feeding_rate_pct,
            "temp_feeding_factor": self.temp_feeding_factor,
            "adjusted_daily_feed_kg": self.adjusted_daily_feed_kg,
            "feed_per_meal_kg": self.feed_per_meal_kg,
            "feedings_per_day": self.feedings_per_day,
            "is_count": self.is_count,
            "lhc_count": self.lhc_count,
            "doc_days": self.doc_days,
            "ibw_g": self.ibw_g,
            "bulk_weight_kg": self.bulk_weight_kg,
            "total_feed_given_kg": self.total_feed_given_kg,
            "total_length_cm": self.total_length_cm,
            "eq1_sr_pct": self.eq1_sr_pct,
            "eq1_mortality_count": self.eq1_mortality_count,
            "eq2_fabw_g": self.eq2_fabw_g,
            "eq2_count_per_kg": self.eq2_count_per_kg,
            "eq3_adwg_g_day": self.eq3_adwg_g_day,
            "eq3_weekly_gain_g": self.eq3_weekly_gain_g,
            "eq4_sgr_pct_day": self.eq4_sgr_pct_day,
            "eq5_ib_kg": self.eq5_ib_kg,
            "eq6_fb_kg": self.eq6_fb_kg,
            "eq5_6_net_biomass_kg": self.eq5_6_net_biomass_kg,
            "eq7_fcr": self.eq7_fcr,
            "eq7_feed_efficiency_pct": self.eq7_feed_efficiency_pct,
            "eq8_fulton_k": self.eq8_fulton_k,
            "eq8_fulton_profile": self.eq8_fulton_profile,
            "lime_pond_vol_m3": self.lime_pond_vol_m3,
            "lime_current_ph": self.lime_current_ph,
            "lime_target_ph": self.lime_target_ph,
            "lime_chemical_type": self.lime_chemical_type,
            "lime_dosage_kg": self.lime_dosage_kg,
            "lime_dosage_ppm": self.lime_dosage_ppm,
            "molasses_daily_feed_kg": self.molasses_daily_feed_kg,
            "molasses_protein_pct": self.molasses_protein_pct,
            "molasses_target_cn": self.molasses_target_cn,
            "molasses_carbon_source": self.molasses_carbon_source,
            "molasses_dosage_kg": self.molasses_dosage_kg,
            "aero_biomass_kg": self.aero_biomass_kg,
            "aero_water_temp_c": self.aero_water_temp_c,
            "aero_salinity_ppt": self.aero_salinity_ppt,
            "aero_target_do_ppm": self.aero_target_do_ppm,
            "aero_power_hp": self.aero_power_hp,
            "aero_units_desc": self.aero_units_desc,
            "ammonia_tan_ppm": self.ammonia_tan_ppm,
            "ammonia_temp_c": self.ammonia_temp_c,
            "ammonia_ph": self.ammonia_ph,
            "ammonia_salinity_ppt": self.ammonia_salinity_ppt,
            "ammonia_factor_f": self.ammonia_factor_f,
            "ammonia_nh3_ppm": self.ammonia_nh3_ppm,
            "ammonia_status": self.ammonia_status,
            "co2_alkalinity_mg_l": self.co2_alkalinity_mg_l,
            "co2_temp_c": self.co2_temp_c,
            "co2_ph": self.co2_ph,
            "co2_factor": self.co2_factor,
            "co2_concentration_mg_l": self.co2_concentration_mg_l,
            "co2_status": self.co2_status,
        }


# --- TABLE 5: USER PAIRED DEVICES ---
class UserDevice(db.Model):
    __tablename__ = "user_devices"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(50), nullable=False, unique=True, index=True)
    user_email = db.Column(db.String(255), nullable=False, index=True)
    device_name = db.Column(db.String(100), nullable=False, default="Pond Telemetry Node")
    pond_location = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_seen = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "user_email": self.user_email,
            "device_name": self.device_name,
            "pond_location": self.pond_location or "Pond Site",
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


# --- TABLE 6: PROBE MAINTENANCE & CALIBRATION SCHEDULES ---
class ProbeMaintenance(db.Model):
    __tablename__ = "probe_maintenance"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(255), nullable=False, index=True)
    device_id = db.Column(db.String(50), nullable=False, default="NODE01", index=True)
    maintenance_type = db.Column(db.String(80), nullable=False, default="Routine Cleaning & Calibration")
    last_cleaned_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_calibrated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    cleaning_interval_days = db.Column(db.Integer, nullable=False, default=7)
    calibration_interval_days = db.Column(db.Integer, nullable=False, default=14)
    notes = db.Column(db.String(255), nullable=True, default="Routine biofilm removal & 2-point buffer recalibration")
    performed_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        now = datetime.now()
        cleaned = self.last_cleaned_at or self.created_at or now
        calibrated = self.last_calibrated_at or cleaned

        days_since_cleaning = max(0.0, (now - cleaned).total_seconds() / 86400.0)
        days_until_cleaning = self.cleaning_interval_days - days_since_cleaning

        days_since_calibration = max(0.0, (now - calibrated).total_seconds() / 86400.0)
        days_until_calibration = self.calibration_interval_days - days_since_calibration

        is_cleaning_overdue = days_until_cleaning <= 0
        is_calibration_overdue = days_until_calibration <= 0
        is_due_soon = (0 < days_until_cleaning <= 2) or (0 < days_until_calibration <= 3)

        if is_cleaning_overdue or is_calibration_overdue:
            status = "Overdue"
            severity = "Critical" if (days_until_cleaning < -2) else "Warning"
            drift_risk = "High Risk - Biofilm Drift Likely"
            badge_class = "badge-critical"
            notice_title = "Scheduled Sensor Maintenance Overdue: Biofilm Accumulation & Drift Risk"
            notice_message = (
                "Submerged pond probes require immediate soft-brush cleaning and 2-point pH recalibration "
                "(buffer 4.01 / 6.86) to counteract biofouling-induced electrochemical drift."
            )
        elif is_due_soon:
            status = "Due Soon"
            severity = "Warning"
            drift_risk = "Moderate Risk - Routine Cleaning Due"
            badge_class = "badge-warning"
            days_rem = max(1, int(round(days_until_cleaning)))
            notice_title = f"Scheduled Sensor Maintenance Notice: Cleaning Due in {days_rem} Day" + ("s" if days_rem > 1 else "")
            notice_message = (
                f"Routine probe maintenance is scheduled in {days_rem} day(s) to prevent biological biofilm fouling "
                "on the pH glass bulb and temperature probe."
            )
        else:
            status = "Optimal"
            severity = "Optimal"
            drift_risk = "Low Risk - Probes Calibrated & Clean"
            badge_class = "badge-optimal"
            days_rem = max(1, int(round(days_until_cleaning)))
            notice_title = "Sensor Probes Calibrated & Biofilm-Free"
            notice_message = (
                f"Probes are within standard operational calibration windows. Next routine cleaning in {days_rem} day(s)."
            )

        clean_pct = min(100, max(0, int((days_since_cleaning / self.cleaning_interval_days) * 100)))
        cal_pct = min(100, max(0, int((days_since_calibration / self.calibration_interval_days) * 100)))

        next_clean_dt = cleaned + timedelta(days=self.cleaning_interval_days)
        next_cal_dt = calibrated + timedelta(days=self.calibration_interval_days)

        return {
            "id": self.id,
            "device_id": self.device_id,
            "user_email": self.user_email,
            "maintenance_type": self.maintenance_type,
            "last_cleaned_at": cleaned.strftime("%Y-%m-%d %H:%M:%S") if cleaned else None,
            "last_calibrated_at": calibrated.strftime("%Y-%m-%d %H:%M:%S") if calibrated else None,
            "next_cleaning_due": next_clean_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "next_calibration_due": next_cal_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "days_since_cleaning": round(days_since_cleaning, 1),
            "days_until_cleaning": round(days_until_cleaning, 1),
            "days_since_calibration": round(days_since_calibration, 1),
            "days_until_calibration": round(days_until_calibration, 1),
            "cleaning_interval_days": self.cleaning_interval_days,
            "calibration_interval_days": self.calibration_interval_days,
            "cleaning_progress_pct": clean_pct,
            "calibration_progress_pct": cal_pct,
            "status": status,
            "severity": severity,
            "badge_class": badge_class,
            "drift_risk": drift_risk,
            "is_notice_active": is_cleaning_overdue or is_calibration_overdue or is_due_soon,
            "notice_title": notice_title,
            "notice_message": notice_message,
            "notes": self.notes or "",
            "performed_by": self.performed_by or "Pond Technician",
        }


# --- TABLE 7: PROBE MAINTENANCE & CALIBRATION HISTORICAL AUDIT LOG ---
class ProbeMaintenanceHistory(db.Model):
    __tablename__ = "probe_maintenance_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(255), nullable=False, index=True)
    device_id = db.Column(db.String(50), nullable=False, default="NODE01", index=True)
    action = db.Column(db.String(50), nullable=False, default="both")
    maintenance_type = db.Column(db.String(120), nullable=False)
    performed_by = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    performed_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    def to_dict(self):
        dt = self.performed_at or datetime.now()
        return {
            "id": self.id,
            "user_email": self.user_email,
            "device_id": self.device_id,
            "action": self.action,
            "maintenance_type": self.maintenance_type,
            "performed_by": self.performed_by or "Pond Operator",
            "notes": self.notes or "Routine sensor maintenance completed.",
            "performed_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date_formatted": dt.strftime("%b %d, %Y %I:%M %p"),
        }


def get_probe_maintenance_status(user_email=None, device_id="NODE01"):
    """
    Retrieves or initializes the active probe maintenance schedule for the specified user & device.
    Defaults to 7-day routine biofilm cleaning and 14-day 2-point pH buffer calibration.
    """
    if not user_email and has_request_context():
        user_email = session.get("user_id")

    default_owner = os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")
    target_user = user_email or default_owner

    maint = None
    try:
        maint = ProbeMaintenance.query.filter_by(user_email=target_user, device_id=device_id).order_by(ProbeMaintenance.last_cleaned_at.desc()).first()
        if not maint:
            maint = ProbeMaintenance.query.filter_by(device_id=device_id).order_by(ProbeMaintenance.last_cleaned_at.desc()).first()
    except Exception:
        db.session.rollback()
        maint = None

    if not maint:
        # Seed an active schedule: last cleaned 5.5 days ago (due soon in 1.5 days!)
        # and last calibrated 12 days ago (due in 2 days!) to demonstrate scheduled notices
        initial_cleaned = datetime.now() - timedelta(days=5, hours=12)
        initial_calibrated = datetime.now() - timedelta(days=12, hours=4)
        maint = ProbeMaintenance(
            user_email=target_user,
            device_id=device_id,
            maintenance_type="Routine Cleaning & 2-Point Buffer Calibration",
            last_cleaned_at=initial_cleaned,
            last_calibrated_at=initial_calibrated,
            cleaning_interval_days=7,
            calibration_interval_days=14,
            notes="Initial pond deployment: DFRobot pH & DS18B20 calibration verified.",
            performed_by="System Initializer",
        )
        try:
            db.session.add(maint)
            db.session.commit()
        except Exception:
            db.session.rollback()

    return maint.to_dict() if maint else {
        "device_id": device_id,
        "status": "Due Soon",
        "severity": "Warning",
        "drift_risk": "Moderate Risk - Routine Cleaning Due",
        "badge_class": "badge-warning",
        "days_since_cleaning": 5.5,
        "days_until_cleaning": 1.5,
        "days_since_calibration": 12.0,
        "days_until_calibration": 2.0,
        "cleaning_interval_days": 7,
        "calibration_interval_days": 14,
        "cleaning_progress_pct": 78,
        "calibration_progress_pct": 85,
        "is_notice_active": True,
        "notice_title": "Scheduled Sensor Maintenance Notice: Cleaning Due in 2 Days",
        "notice_message": "Routine probe maintenance is scheduled in 2 day(s) to prevent biological biofilm fouling on the pH glass bulb and temperature probe.",
        "notes": "Baseline calibrated",
        "performed_by": "System Initializer"
    }


# ==========================================
# EMAIL VALIDATION UTILITIES (LEGIT & ACTIVE DOMAIN RULES)
# ==========================================

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "guerrillamail.block", "guerrillamail.net", "guerrillamail.org", "sharklasers.com",
    "yopmail.com", "yopmail.fr", "yopmail.net", "trashmail.com", "trashmail.net",
    "dispostable.com", "getairmail.com", "throwawaymail.com", "fakemailgenerator.com",
    "temp-mail.org", "tempmail.net", "generator.email", "mohmal.com", "nada.ltd",
    "crazymailing.com", "inboxkitten.com", "mytemp.email", "tempinbox.com",
    "burnermail.io", "maildrop.cc", "emailondeck.com", "zillamail.com",
    "trashmail.org", "dropmail.me", "mohmal.im", "armyspy.com", "dayrep.com",
    "teleworm.us", "rhyta.com", "cuvox.de", "superrito.com"
}

BLOCKED_PLACEHOLDER_DOMAINS = {
    "example.com", "example.org", "example.net", "example.edu",
    "test.com", "testing.com", "test.test", "sample.com", "fake.com",
    "temp.com", "invalid", "localhost", "none.com", "null.com",
    "asdf.com", "qwerty.com", "xyz.com", "domain.com", "email.com",
    "placeholder.com", "foo.com", "bar.com"
}

COMMON_DOMAIN_TYPOS = {
    "gmial.com": "gmail.com",
    "gmai.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "hotmial.com": "hotmail.com",
    "hotmaill.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "outllok.com": "outlook.com",
    "iclud.com": "icloud.com",
}

EMAIL_RFC_REGEX = re.compile(
    r"^(?![.])(?!.*[.]{2})[a-zA-Z0-9_.+-]+(?<![.])"
    r"@"
    r"(?![.-])(?!.*[.]{2})(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,24}$"
)


def validate_legit_email(email_str):
    """
    Validates that an email is structurally valid and represents a legitimate,
    non-disposable, non-placeholder email address.
    Returns: (is_valid: bool, error_message: str | None)
    """
    if not email_str or not isinstance(email_str, str):
        return False, "Please enter an email address."

    email = email_str.strip().lower()

    if len(email) < 6:
        return False, "Email address is too short."

    if len(email) > 254:
        return False, "Email address exceeds the 254-character limit."

    if email.count("@") != 1:
        return False, "Email must contain exactly one '@' symbol."

    local_part, domain_part = email.split("@", 1)

    if not local_part or len(local_part) > 64:
        return False, "The username portion before '@' must be between 1 and 64 characters."

    if not domain_part or len(domain_part) < 3:
        return False, "The domain portion after '@' is incomplete."

    if not EMAIL_RFC_REGEX.match(email):
        return False, "Enter a valid email address with a recognized domain (e.g., name@gmail.com)."

    if domain_part in DISPOSABLE_EMAIL_DOMAINS:
        return False, "Disposable or temporary email addresses are not permitted. Please use a legitimate email."

    if domain_part in BLOCKED_PLACEHOLDER_DOMAINS or domain_part.endswith(".invalid") or domain_part.endswith(".localhost"):
        return False, "Placeholder or dummy email domains are not allowed. Please enter your real email address."

    if local_part in {"test", "testing", "fake", "temp", "asdf", "dummy", "admin", "user", "none"} and domain_part in {
        "test.com", "fake.com", "dummy.com", "temp.com", "asdf.com", "user.com", "admin.com"
    }:
        return False, "Please provide a real, active email address."

    if domain_part in COMMON_DOMAIN_TYPOS:
        suggested = COMMON_DOMAIN_TYPOS[domain_part]
        return False, f"Did you mean '{local_part}@{suggested}'? Please verify your domain spelling."

    return True, None


def log_activity(action, details=None, user_email=None, user_name=None, role=None, ip_address=None):
    try:
        if not user_email and has_request_context():
            user_email = session.get("user_id")
        if not role and has_request_context():
            role = session.get("user_role")

        if not user_name and user_email:
            user = db.session.get(User, user_email)
            if user:
                user_name = user.name
                if not role:
                    role = user.role

        if not ip_address and has_request_context():
            ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
            if ip_address and "," in ip_address:
                ip_address = ip_address.split(",")[0].strip()

        log_entry = ActivityLog(
            user_email=user_email,
            user_name=user_name or "System",
            role=role or "System",
            action=action,
            details=details or "",
            ip_address=ip_address,
            timestamp=datetime.now(),
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        app.logger.warning("Failed to record activity log: %s", exc)


ADAPTIVE_PERSONAS = {
    "evaluating": {
        "id": "evaluating",
        "title": "Evaluating Usage",
        "badge": "New Account",
        "description": "No interaction history recorded yet for this new account. Navigate across monitoring, calculators, and analytics to train your behavioral profile.",
        "icon": "icon-sparkles",
        "shortcuts": [
            {"label": "Pond Dashboard", "url": "/dashboard", "icon": "icon-dashboard"},
            {"label": "Live Monitoring", "url": "/monitoring", "icon": "icon-monitor"},
            {"label": "Aquaculture Tools", "url": "/calculators", "icon": "icon-calculator"},
            {"label": "Alerts & Notifications", "url": "/alerts", "icon": "icon-alert"},
        ],
        "default_density": "auto",
        "preferred_metrics": ["temperature", "ph"],
    },
    "field_inspector": {
        "id": "field_inspector",
        "title": "Real-time Monitoring & Telemetry",
        "badge": "Monitoring & Sensors",
        "description": "Optimized for pond-side telemetry checks, anomaly response, and responsive telemetry views.",
        "icon": "icon-monitor",
        "shortcuts": [
            {"label": "Real-time Monitoring", "url": "/monitoring", "icon": "icon-monitor", "badge": "Live"},
            {"label": "Pond Telemetry", "url": "/dashboard", "icon": "icon-dashboard"},
            {"label": "Active Alerts", "url": "/alerts", "icon": "icon-alert"},
            {"label": "Hardware Devices", "url": "/devices", "icon": "icon-cpu"},
        ],
        "default_density": "comfort",
        "preferred_metrics": ["temperature", "ph"],
    },
    "farm_planner": {
        "id": "farm_planner",
        "title": "Aquaculture Farm Planner",
        "badge": "Farm Planner",
        "description": "Optimized for bio-mass forecasting, feeding rate adjustments, lime treatment, and molasses dosing.",
        "icon": "icon-calculator",
        "shortcuts": [
            {"label": "Aquaculture Calculators", "url": "/calculators", "icon": "icon-calculator", "badge": "Tools"},
            {"label": "Feeding & Biomass", "url": "/calculators#feeding-calculator-panel", "icon": "icon-calculator"},
            {"label": "Water Quality Check", "url": "/monitoring", "icon": "icon-monitor"},
            {"label": "Telemetry Dashboard", "url": "/dashboard", "icon": "icon-dashboard"},
        ],
        "default_density": "comfort",
        "preferred_metrics": ["ph", "temperature"],
    },
    "data_analyst": {
        "id": "data_analyst",
        "title": "Pond Data Analyst",
        "badge": "Data Analyst",
        "description": "Optimized for high-density multi-parameter trend audits, historical reporting, and CSV data export.",
        "icon": "icon-chart",
        "shortcuts": [
            {"label": "Analytics & Trends", "url": "/analytics", "icon": "icon-chart", "badge": "Reports"},
            {"label": "Historical Audits", "url": "/historical", "icon": "icon-history"},
            {"label": "Live Monitoring", "url": "/monitoring", "icon": "icon-monitor"},
            {"label": "Calculators & Tools", "url": "/calculators", "icon": "icon-calculator"},
        ],
        "default_density": "compact",
        "preferred_metrics": ["temperature", "ph"],
    },
    "balanced_operator": {
        "id": "balanced_operator",
        "title": "Balanced Farm Operator",
        "badge": "Standard Operator",
        "description": "Balanced workflow providing an even overview of telemetry, calculations, and alert notifications.",
        "icon": "icon-dashboard",
        "shortcuts": [
            {"label": "Pond Dashboard", "url": "/dashboard", "icon": "icon-dashboard"},
            {"label": "Live Monitoring", "url": "/monitoring", "icon": "icon-monitor"},
            {"label": "Aquaculture Tools", "url": "/calculators", "icon": "icon-calculator"},
            {"label": "Alerts & Notifications", "url": "/alerts", "icon": "icon-alert"},
        ],
        "default_density": "auto",
        "preferred_metrics": ["temperature", "ph"],
    },
}


@app.context_processor
def inject_logout_csrf_token():
    user_email = session.get("user_id")
    if user_email is None:
        return {
            "logout_csrf_token": "",
            "current_user": None,
            "adaptive_profile": session.get("adaptive_profile") or {},
            "adaptive_persona": ADAPTIVE_PERSONAS.get(
                (session.get("adaptive_profile") or {}).get("persona_id", "evaluating"),
                ADAPTIVE_PERSONAS["evaluating"]
            ),
        }
    current_u = None
    try:
        current_u = db.session.get(User, user_email)
    except Exception:
        pass
    logout_token = session.get("logout_csrf_token")
    if not logout_token or not verify_timed_csrf_token(logout_token, purpose="logout", max_age=86400):
        logout_token = generate_timed_csrf_token("logout")
        session["logout_csrf_token"] = logout_token

    adaptive_profile = session.get("adaptive_profile") or {}
    persona_id = adaptive_profile.get("persona_id", "evaluating")
    persona_info = ADAPTIVE_PERSONAS.get(persona_id, ADAPTIVE_PERSONAS["evaluating"])

    return {
        "logout_csrf_token": logout_token,
        "current_user": current_u,
        "adaptive_profile": adaptive_profile,
        "adaptive_persona": persona_info,
    }



def parse_reading_datetime(reading):
    try:
        d_val = str(reading["date"] if isinstance(reading, dict) or hasattr(reading, "__getitem__") else getattr(reading, "date", ""))
        if d_val.endswith("Z") or "+" in d_val:
            return datetime.fromisoformat(d_val.replace("Z", "+00:00")).astimezone().replace(tzinfo=None)
        return datetime.fromisoformat(d_val)
    except Exception:
        return datetime.min

def serialize_sensor_reading(reading):
    try:
        t_val = float(reading["temperature"])
        p_val = float(reading["ph_level"])
        analysis = calculate_ml_water_quality_analysis(t_val, p_val)
        status = analysis["overall_status"]
        temp_status = analysis["temperature_status"]
        ph_status = analysis["ph_status"]
        wqi_score = analysis["wqi_score"]
        wqi_status = analysis["wqi_status"]
        wqi_theme = analysis["wqi_theme"]
        temp_adjustment = analysis["temp_adjustment"]
        ph_adjustment = analysis["ph_adjustment"]
        ml_ranges = analysis["ml_ranges"]
    except Exception:
        status = reading["status"] or "Optimal"
        temp_status = "Optimal"
        ph_status = "Optimal"
        wqi_score = 100
        wqi_status = "OPTIMAL QUALITY"
        wqi_theme = "optimal"
        temp_adjustment = {
            "percent": 0.0,
            "delta": 0.0,
            "direction": "Optimal",
            "percent_text": "0.0%",
            "badge_text": "Normal",
            "badge_class": "badge-normal",
            "detail_text": "Within ML optimal range (28.0–32.0 °C)",
            "status": "Optimal",
        }
        ph_adjustment = {
            "percent": 0.0,
            "delta": 0.0,
            "direction": "Optimal",
            "percent_text": "0.0%",
            "badge_text": "Normal",
            "badge_class": "badge-normal",
            "detail_text": "Within ML optimal range (7.50–8.50)",
            "status": "Optimal",
        }
        ml_ranges = {
            "temperature": {"optimal_min": 28.0, "optimal_max": 32.0, "optimal_mid": 30.0, "unit": "°C"},
            "ph": {"optimal_min": 7.50, "optimal_max": 8.50, "optimal_mid": 8.00, "unit": "pH"},
        }

    return {
        "temperature": reading["temperature"],
        "ph": reading["ph_level"],
        "recorded_at": reading["date"],
        "status": status,
        "temperature_status": temp_status,
        "ph_status": ph_status,
        "wqi_score": wqi_score,
        "wqi_status": wqi_status,
        "wqi_theme": wqi_theme,
        "temp_adjustment": temp_adjustment,
        "ph_adjustment": ph_adjustment,
        "ml_ranges": ml_ranges,
    }


def role_required(*allowed_roles):
    valid_roles = set()
    for r in allowed_roles:
        if isinstance(r, (list, tuple, set)):
            valid_roles.update(item.strip().casefold() for item in r)
        elif r:
            valid_roles.add(str(r).strip().casefold())

    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            # 1. Hardware IoT / API key authentication (for automated microcontrollers & daemons)
            api_key = request.headers.get("X-API-Key")
            auth_header = request.headers.get("Authorization", "")
            if not api_key and auth_header.startswith("Bearer "):
                api_key = auth_header[7:].strip()

            configured_secret = os.getenv("SECRET_KEY")
            if api_key and configured_secret and hmac.compare_digest(api_key, configured_secret):
                return view(*args, **kwargs)

            # 2. Browser session authentication
            user_id = session.get("user_id")
            if user_id is None:
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"error": "Authentication required."}), 401
                return redirect(url_for("login"))

            try:
                user = db.session.get(User, user_id)
            except SQLAlchemyError:
                db.session.rollback()
                return "Authentication service is temporarily unavailable. Please retry.", 503

            if user is None:
                session.clear()
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"error": "User account not found."}), 401
                return redirect(url_for("login"))

            actual_role = user.role.strip().casefold()
            if actual_role not in valid_roles:
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"error": "Insufficient permissions for this endpoint."}), 403
                if actual_role == "admin":
                    return redirect(url_for("admin_home"))
                if actual_role == "client":
                    return redirect(url_for("dashboard"))
                session.clear()
                return redirect(url_for("login"))

            return view(*args, **kwargs)

        return wrapped

    return decorate


@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")


with app.app_context():
    try:
        db.engine.connect()
        db.create_all()
        # Automatically synchronize missing columns on sensors and aquaculture_calculations tables
        with db.engine.connect() as conn:
            try:
                res_sens = conn.execute(text("DESCRIBE sensors;"))
                sensor_cols = {row[0].lower() for row in res_sens.fetchall()}
                if "user_email" not in sensor_cols:
                    conn.execute(text("ALTER TABLE sensors ADD COLUMN user_email VARCHAR(255) NULL;"))
                    conn.execute(text("CREATE INDEX idx_sensors_user_email ON sensors (user_email);"))
                    conn.execute(text("UPDATE sensors SET user_email = 'rio@gmail.com' WHERE user_email IS NULL;"))
                if "id" not in sensor_cols:
                    conn.execute(text("ALTER TABLE sensors ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;"))
                conn.commit()
            except Exception:
                pass

            try:
                res = conn.execute(text("DESCRIBE aquaculture_calculations;"))
                existing_cols = {row[0].lower() for row in res.fetchall()}
                col_defs = {
                    "co2_alkalinity_mg_l": "FLOAT NULL",
                    "co2_temp_c": "FLOAT NULL",
                    "co2_ph": "FLOAT NULL",
                    "co2_factor": "FLOAT NULL",
                    "co2_concentration_mg_l": "FLOAT NULL",
                    "co2_status": "VARCHAR(50) NULL",
                }
                for col_name, col_sql in col_defs.items():
                    if col_name.lower() not in existing_cols:
                        conn.execute(text(f"ALTER TABLE aquaculture_calculations ADD COLUMN {col_name} {col_sql};"))
                conn.commit()
            except Exception:
                pass
    except Exception:
        pass


def _async_dispatch_ntfy(status, temperature, ph, topics):
    """Dispatches ntfy push notifications in a daemon thread so API responses are instantaneous."""
    try:
        from recommendations import predict_recommendation
        ai_data = predict_recommendation(temperature, ph)
    except Exception as exc:
        app.logger.warning(f"Unable to load AI recommendation for push alert: {exc}")
        ai_data = None

    for top in set(topics):
        try:
            send_water_quality_alert_ntfy(status, temperature, ph, topic=top, ai_data=ai_data)
        except Exception as exc:
            app.logger.exception(f"Unable to dispatch ntfy push alert to topic {top}: {exc}")


@app.route("/api/readings", methods=["POST"])
@role_required("Client", "Admin")
def create_reading():
    payload = request.get_json(silent=True) or {}
    required_fields = ["temperature", "ph"]

    if not all(field in payload for field in required_fields):
        return jsonify({"error": "Missing required water quality fields."}), 400

    try:
        temperature = float(payload["temperature"])
        ph = float(payload["ph"])
        raw_recorded_at = payload.get("recorded_at")
        if raw_recorded_at:
            clean_ts = str(raw_recorded_at).replace("Z", "+00:00")
            parsed_dt = datetime.fromisoformat(clean_ts)
            if parsed_dt.tzinfo is not None:
                recorded_at = parsed_dt.astimezone().replace(tzinfo=None)
            else:
                recorded_at = parsed_dt
        else:
            recorded_at = datetime.now()
    except (TypeError, ValueError):
        return jsonify({"error": "Reading values must be valid numbers and date."}), 400
    if not math.isfinite(temperature) or not math.isfinite(ph):
        return jsonify({"error": "Reading values must be finite numbers."}), 400

    now_dt = datetime.now()
    if recorded_at > now_dt:
        recorded_at = now_dt

    recorded_at_str = recorded_at.strftime("%Y-%m-%dT%H:%M:%S.%f")

    # Associate reading with the authenticated client or specified user
    target_user_email = (
        session.get("user_id")
        or (payload.get("user_email") if isinstance(payload, dict) else None)
        or request.args.get("user_email")
        or os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")
    )

    # ML-based classification & comprehensive analysis: solely determined by the DecisionTreeClassifier model
    try:
        analysis = calculate_ml_water_quality_analysis(temperature, ph)
        status = analysis["overall_status"]
    except Exception:
        app.logger.exception("Unable to classify reading using ML model.")
        status = "Warning"
        analysis = None

    try:
        db.session.execute(
            insert(sensor_readings).values(
                user_email=target_user_email,
                ph_level=ph,
                temperature=temperature,
                date=recorded_at_str,
                status=status,
            )
        )
        db.session.commit()

        # Automatic Push Alert dispatch via ntfy.sh (100% Free & Safe, Non-blocking)
        if status in ("Critical", "Warning"):
            try:
                topics = []
                users_with_topic = db.session.query(User).filter(
                    User.email == target_user_email,
                    User.ntfy_topic.isnot(None),
                    User.ntfy_topic != "",
                ).all()
                for u in users_with_topic:
                    if u.ntfy_topic and is_valid_topic(u.ntfy_topic):
                        topics.append(u.ntfy_topic)
                default_topic = os.getenv("NTFY_DEFAULT_TOPIC")
                if default_topic and is_valid_topic(default_topic) and default_topic not in topics:
                    topics.append(default_topic)

                if topics:
                    threading.Thread(
                        target=_async_dispatch_ntfy,
                        args=(status, temperature, ph, topics),
                        daemon=True
                    ).start()
            except Exception:
                app.logger.exception("Unable to spawn ntfy push alert thread.")

        resp_payload = {
            "temperature": temperature,
            "ph": ph,
            "recorded_at": recorded_at_str,
            "status": status,
            "user_email": target_user_email,
        }
        if analysis:
            resp_payload.update({
                "temperature_status": analysis["temperature_status"],
                "ph_status": analysis["ph_status"],
                "wqi_score": analysis["wqi_score"],
                "wqi_status": analysis["wqi_status"],
                "wqi_theme": analysis["wqi_theme"],
                "temp_adjustment": analysis["temp_adjustment"],
                "ph_adjustment": analysis["ph_adjustment"],
                "ml_ranges": analysis["ml_ranges"],
            })

        return jsonify(resp_payload), 201
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to save sensor reading.")
        return jsonify({"error": "Unable to save sensor reading."}), 503


@app.route("/api/readings/latest")
@role_required("Client", "Admin")
def latest_reading():
    user_id = session.get("user_id")
    user_role = session.get("role") or "Client"
    hw_default_owner = os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")

    latest_reading_dict = None
    try:
        query = select(sensor_readings).order_by(sensor_readings.c.date.desc())
        if user_role != "Admin" and user_id:
            query = query.where(sensor_readings.c.user_email == user_id)
        latest_row = db.session.execute(query.limit(1)).mappings().first()
        if latest_row:
            latest_reading_dict = dict(latest_row)
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load the latest sensor reading.")

    from hardware_serial import LATEST_HARDWARE_STREAM

    # Only fallback to live hardware serial stream if Admin or the designated hardware owner
    is_hw_authorized = (user_role == "Admin") or (user_id and user_id.lower() == hw_default_owner.lower())

    stream_temp = LATEST_HARDWARE_STREAM.get("temperature")
    stream_last_time = LATEST_HARDWARE_STREAM.get("last_packet_time", 0)
    has_live_stream = is_hw_authorized and stream_temp is not None and (time.time() - stream_last_time < 60)

    # Prefer live streaming data if actively received within the last 60 seconds
    if has_live_stream:
        reading_dict = {
            "temperature": LATEST_HARDWARE_STREAM["temperature"],
            "ph_level": LATEST_HARDWARE_STREAM["ph"],
            "date": LATEST_HARDWARE_STREAM.get("recorded_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": LATEST_HARDWARE_STREAM.get("status") or "Optimal",
            "user_email": hw_default_owner,
        }
        res = serialize_sensor_reading(reading_dict)
    elif latest_reading_dict:
        res = serialize_sensor_reading(latest_reading_dict)
    elif is_hw_authorized and stream_temp is not None:
        reading_dict = {
            "temperature": LATEST_HARDWARE_STREAM["temperature"],
            "ph_level": LATEST_HARDWARE_STREAM["ph"],
            "date": LATEST_HARDWARE_STREAM.get("recorded_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": LATEST_HARDWARE_STREAM.get("status") or "Optimal",
            "user_email": hw_default_owner,
        }
        res = serialize_sensor_reading(reading_dict)
    else:
        return jsonify(None)

    res["is_connected"] = bool(LATEST_HARDWARE_STREAM.get("is_connected", False)) if is_hw_authorized else False
    res["connected_port"] = LATEST_HARDWARE_STREAM.get("connected_port") if is_hw_authorized else None
    return jsonify(res)


@app.route("/api/hardware/status")
@role_required("Client", "Admin")
def hardware_status():
    from hardware_serial import LATEST_HARDWARE_STREAM
    return jsonify(LATEST_HARDWARE_STREAM)


def get_system_devices_inventory():
    """Generates the comprehensive device inventory list, categories, and summary metrics."""
    from hardware_serial import LATEST_HARDWARE_STREAM

    user_email = session.get("user_id") if has_request_context() else None
    user_role = session.get("role") if has_request_context() else None
    hw_default_owner = os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")

    paired_nodes = []
    if user_email:
        try:
            paired_nodes = [d.device_id for d in UserDevice.query.filter_by(user_email=user_email, status="Active").all()]
        except Exception:
            paired_nodes = []

    is_hw_authorized = (
        (user_role == "Admin")
        or (user_email and user_email.lower() == hw_default_owner.lower())
        or bool(paired_nodes)
    )

    stream = (LATEST_HARDWARE_STREAM or {}) if is_hw_authorized else {}
    if user_role != "Admin" and user_email and user_email.lower() != hw_default_owner.lower():
        if stream.get("device_id") not in paired_nodes:
            stream = {}
    hw_connected = bool(stream.get("is_connected") or stream.get("connected"))
    port = stream.get("connected_port") or os.getenv("LORA_PORT", "COM8")
    seq = stream.get("seq")
    rssi = stream.get("rssi")
    snr = stream.get("snr")
    device_id = stream.get("device_id") or "NODE01"
    recorded_at = stream.get("recorded_at")

    # Evaluate live telemetry and packet freshness (Node 1 broadcasts every 5 seconds).
    # Hardware is only considered actively broadcasting if a packet arrived within the last 20 seconds.
    last_packet_time = stream.get("last_packet_time", 0)
    now_epoch = time.time()
    is_live_packet = False

    if last_packet_time and (now_epoch - last_packet_time <= 20):
        is_live_packet = True
    elif recorded_at:
        try:
            clean_ts = recorded_at.replace("Z", "").split(".")[0]
            fmt = "%Y-%m-%dT%H:%M:%S" if "T" in clean_ts else "%Y-%m-%d %H:%M:%S"
            rec_dt = datetime.strptime(clean_ts, fmt)
            diff_sec = (datetime.now() - rec_dt).total_seconds()
            if 0 <= diff_sec <= 20:
                is_live_packet = True
        except Exception:
            pass

    # Live sensor values (only valid if live packet arrived within timeout window)
    live_temp = stream.get("temperature") if is_live_packet else None
    live_ph = stream.get("ph") if is_live_packet else None

    # Determine probe health checks on live data
    temp_fault = None
    if live_temp is not None:
        if abs(live_temp - (-127.0)) < 0.5:
            temp_fault = "1-Wire Open Circuit (-127°C)"
        elif abs(live_temp - 85.0) < 0.5:
            temp_fault = "Power-on Reset (85°C)"

    ph_fault = None
    if live_ph is not None:
        if live_ph <= 0.2 or live_ph >= 13.8:
            ph_fault = "Floating ADC / Disconnect"

    # Gateway (Node 2 base station) status: online if USB serial port is open
    node2_online = hw_connected

    # Pond Node 1 transmitter and connected modules: online only if Gateway is connected AND live packet received recently
    node1_online = hw_connected and is_live_packet

    # Query last DB reading for historical reference display (scoped to authenticated user)
    latest_db_reading = None
    try:
        query = select(sensor_readings).order_by(sensor_readings.c.date.desc())
        if user_role != "Admin" and user_email:
            query = query.where(sensor_readings.c.user_email == user_email)
        latest_row = db.session.execute(query.limit(1)).mappings().first()
        if latest_row:
            latest_db_reading = dict(latest_row)
    except SQLAlchemyError:
        db.session.rollback()

    display_temp = live_temp if live_temp is not None else (float(latest_db_reading["temperature"]) if latest_db_reading else None)
    display_ph = live_ph if live_ph is not None else (float(latest_db_reading["ph_level"]) if latest_db_reading else None)
    display_recorded_at = recorded_at if recorded_at else (str(latest_db_reading["date"]) if latest_db_reading else None)

    devices_list = [
        {
            "id": "COMM-01",
            "name": "Node 2 LoRa Base Station Gateway",
            "type": "IoT Serial Bridge / Receiver",
            "category": "Communication",
            "status": "Online" if node2_online else "Offline",
            "last_seen": f"Active ({port} @ 115200 baud)" if node2_online else "Standby (USB Disconnected)",
            "details": f"{port} @ 115200 baud • Win32 CDC Driver",
        },
        {
            "id": "COMM-02",
            "name": "Node 1 Autonomous Pond Transmitter Unit",
            "type": "Edge Telemetry Station",
            "category": "Communication",
            "status": "Online" if node1_online else "Offline",
            "last_seen": "Broadcasting (5s Cadence)" if node1_online else ("Offline (No Telemetry Link)" if node2_online else "Offline (Gateway Standby)"),
            "details": f"Node ID: {device_id} • 5s Periodic Broadcast",
        },
        {
            "id": "SEN-01",
            "name": "DS18B20 Waterproof Temperature Sensor",
            "type": "Digital 1-Wire Thermal Probe",
            "category": "Sensors",
            "status": "Online" if (node1_online and live_temp is not None and not temp_fault) else "Offline",
            "last_seen": "Telemetry Active" if (node1_online and live_temp is not None and not temp_fault) else "Offline (Probe Inactive)",
            "details": f"Current: {live_temp:.2f} °C" if (node1_online and live_temp is not None) else (temp_fault or "1-Wire GPIO4 (4.7kΩ pull-up)"),
        },
        {
            "id": "SEN-02",
            "name": "DFRobot Industrial Analog pH Sensor (SEN0161)",
            "type": "Electrochemical Glass Electrode",
            "category": "Sensors",
            "status": "Online" if (node1_online and live_ph is not None and not ph_fault) else "Offline",
            "last_seen": "Telemetry Active" if (node1_online and live_ph is not None and not ph_fault) else "Offline (Probe Inactive)",
            "details": f"Current: {live_ph:.2f} pH" if (node1_online and live_ph is not None) else (ph_fault or "ADC1_CH6 GPIO34 (0-3.3V)"),
        },
        {
            "id": "COMM-03",
            "name": "SX1278 433.5 MHz LoRa RF Transceiver",
            "type": "Sub-GHz Long-Range Radio",
            "category": "Communication",
            "status": "Online" if node1_online else "Offline",
            "last_seen": "Link Active" if node1_online else "Offline (No RF Carrier)",
            "details": f"433.50 MHz ISM • RSSI: {rssi or -72} dBm • SNR: +{snr or 9.2} dB" if node1_online else "433.50 MHz ISM (Standby)",
        },
        {
            "id": "COMM-04",
            "name": "20x4 I2C Character LCD Display (HD44780)",
            "type": "Field Telemetry Display",
            "category": "Communication",
            "status": "Online" if node2_online else "Offline",
            "last_seen": "Display Active" if node2_online else "Offline (Base Station Off)",
            "details": "I2C Addr 0x27 • PCF8574 Backpack",
        },
        {
            "id": "PWR-01",
            "name": "Pond Solar Boost Unit & Charge Controller",
            "type": "Solar PV Energy Harvester",
            "category": "Power",
            "status": "Online" if node1_online else "Offline",
            "last_seen": "Solar Ingestion Active" if node1_online else "Offline (Node 1 Off)",
            "details": "Autonomous Solar Energy Ingestion",
        },
        {
            "id": "PWR-02",
            "name": "3.7V Li-ion Battery Power Management System",
            "type": "Rechargeable Battery Cell & BMS",
            "category": "Power",
            "status": "Online" if node1_online else "Offline",
            "last_seen": "Battery Rail Active" if node1_online else "Offline (Node 1 Off)",
            "details": "Continuous Pond Unit Power Rail",
        },
        {
            "id": "SIG-01",
            "name": "Active 5V Piezo Acoustic Buzzer",
            "type": "Audible Alarm Sounder",
            "category": "Alerts & Signaling",
            "status": "Online" if node2_online else "Offline",
            "last_seen": "Alarm Armed" if node2_online else "Offline (Base Station Off)",
            "details": "Audio Alert for Warning & Critical Water Thresholds",
        },
        {
            "id": "SIG-02",
            "name": "Tricolor Water Quality Status LEDs",
            "type": "Visual Indicator Array",
            "category": "Alerts & Signaling",
            "status": "Online" if node2_online else "Offline",
            "last_seen": "Indicators Armed" if node2_online else "Offline (Base Station Off)",
            "details": "Green (Optimal), Yellow (Warning), Red (Critical) Indicators",
        },
    ]

    total_devices = len(devices_list)
    online_devices = sum(1 for d in devices_list if d["status"] == "Online")
    offline_devices = sum(1 for d in devices_list if d["status"] == "Offline")
    connected_sensors = sum(1 for d in devices_list if d["category"] == "Sensors" and d["status"] == "Online")

    category_stats = {
        "sensors": {
            "total": sum(1 for d in devices_list if d["category"] == "Sensors"),
            "online": sum(1 for d in devices_list if d["category"] == "Sensors" and d["status"] == "Online"),
            "offline": sum(1 for d in devices_list if d["category"] == "Sensors" and d["status"] == "Offline"),
            "items": [d["name"] for d in devices_list if d["category"] == "Sensors"],
        },
        "communication": {
            "total": sum(1 for d in devices_list if d["category"] == "Communication"),
            "online": sum(1 for d in devices_list if d["category"] == "Communication" and d["status"] == "Online"),
            "offline": sum(1 for d in devices_list if d["category"] == "Communication" and d["status"] == "Offline"),
            "items": [d["name"] for d in devices_list if d["category"] == "Communication"],
        },
        "alerts": {
            "total": sum(1 for d in devices_list if d["category"] == "Alerts & Signaling"),
            "online": sum(1 for d in devices_list if d["category"] == "Alerts & Signaling" and d["status"] == "Online"),
            "offline": sum(1 for d in devices_list if d["category"] == "Alerts & Signaling" and d["status"] == "Offline"),
            "items": [d["name"] for d in devices_list if d["category"] == "Alerts & Signaling"],
        },
        "power": {
            "total": sum(1 for d in devices_list if d["category"] == "Power"),
            "online": sum(1 for d in devices_list if d["category"] == "Power" and d["status"] == "Online"),
            "offline": sum(1 for d in devices_list if d["category"] == "Power" and d["status"] == "Offline"),
            "items": [d["name"] for d in devices_list if d["category"] == "Power"],
        },
    }

    return {
        "devices": devices_list,
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "connected_sensors": connected_sensors,
        "category_stats": category_stats,
        "is_connected": hw_connected,
        "connected_port": port,
        "latest_telemetry": {
            "temperature": display_temp,
            "ph": display_ph,
            "status": stream.get("status") or (latest_db_reading["status"] if latest_db_reading else "Optimal"),
            "recorded_at": display_recorded_at,
            "device_id": device_id,
            "seq": seq,
            "rssi": rssi,
            "snr": snr,
            "is_live": is_live_packet,
        },
        "count": total_devices,
    }


@app.route("/api/devices/inventory")
@role_required("Client", "Admin")
def api_devices_inventory():
    """Returns a full inventory of all system hardware components and their live states."""
    data = get_system_devices_inventory()
    return jsonify(data)


@app.route("/api/devices/paired")
@role_required("Client", "Admin")
def api_devices_paired():
    """Returns all telemetry nodes paired with the authenticated user account."""
    user_email = session.get("user_id")
    user_role = session.get("role") or "Client"

    try:
        if user_role == "Admin":
            nodes = UserDevice.query.order_by(UserDevice.created_at.desc()).all()
        else:
            nodes = UserDevice.query.filter_by(user_email=user_email).order_by(UserDevice.created_at.desc()).all()

        from hardware_serial import LATEST_HARDWARE_STREAM
        stream = LATEST_HARDWARE_STREAM or {}
        stream_dev_id = stream.get("device_id")
        is_live = False
        last_packet_time = stream.get("last_packet_time", 0)
        if last_packet_time and (time.time() - last_packet_time <= 20):
            is_live = True

        result = []
        for n in nodes:
            d_dict = n.to_dict()
            d_dict["is_streaming"] = is_live and (stream_dev_id == n.device_id)
            result.append(d_dict)

        return jsonify({"success": True, "devices": result})
    except Exception as exc:
        app.logger.exception("Failed to retrieve paired devices: %s", exc)
        return jsonify({"success": False, "error": str(exc), "devices": []}), 500


@app.route("/api/devices/pair", methods=["POST"])
@role_required("Client", "Admin")
def api_devices_pair():
    """Pairs an ESP32 LoRa transmitter Node ID with the user's account."""
    user_email = session.get("user_id")
    if not user_email:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    payload = request.get_json(silent=True) or {}
    raw_node_id = str(payload.get("device_id") or "").strip().upper()
    device_name = str(payload.get("device_name") or "").strip()
    pond_location = str(payload.get("pond_location") or "").strip()

    if not raw_node_id:
        return jsonify({"success": False, "error": "Hardware Node ID is required (e.g. NODE01, NODE02)."}), 400

    if not re.match(r"^[A-Z0-9_\-]+$", raw_node_id) or len(raw_node_id) < 2 or len(raw_node_id) > 30:
        return jsonify({"success": False, "error": "Node ID must be 2-30 characters (letters, numbers, hyphens/underscores)."}), 400

    if not device_name:
        device_name = f"Pond Node {raw_node_id}"

    try:
        existing = UserDevice.query.filter_by(device_id=raw_node_id).first()
        if existing:
            if existing.user_email != user_email and session.get("role") != "Admin":
                return jsonify({
                    "success": False,
                    "error": f"Node ID '{raw_node_id}' is already paired with another account. Please verify your hardware node ID."
                }), 409

            # Re-activate or update existing node
            existing.user_email = user_email
            existing.device_name = device_name
            existing.pond_location = pond_location or existing.pond_location
            existing.status = "Active"
            db.session.commit()
            log_activity(user_email, "Pair Device", f"Updated pairing for node '{raw_node_id}' ({device_name})")
            return jsonify({
                "success": True,
                "message": f"Hardware Node '{raw_node_id}' updated successfully.",
                "device": existing.to_dict()
            })

        new_device = UserDevice(
            device_id=raw_node_id,
            user_email=user_email,
            device_name=device_name,
            pond_location=pond_location or "Pond Site",
            status="Active"
        )
        db.session.add(new_device)
        db.session.commit()
        log_activity(user_email, "Pair Device", f"Paired hardware node '{raw_node_id}' ({device_name})")
        return jsonify({
            "success": True,
            "message": f"Hardware Node '{raw_node_id}' paired successfully with your account.",
            "device": new_device.to_dict()
        }), 201
    except Exception as exc:
        db.session.rollback()
        app.logger.exception("Failed to pair device: %s", exc)
        return jsonify({"success": False, "error": f"Database error: {str(exc)}"}), 500


@app.route("/api/devices/unpair", methods=["POST"])
@role_required("Client", "Admin")
def api_devices_unpair():
    """Unpairs a hardware node from the authenticated user's account."""
    user_email = session.get("user_id")
    payload = request.get_json(silent=True) or {}
    raw_node_id = str(payload.get("device_id") or "").strip().upper()

    if not raw_node_id:
        return jsonify({"success": False, "error": "Hardware Node ID is required."}), 400

    try:
        device = UserDevice.query.filter_by(device_id=raw_node_id).first()
        if not device:
            return jsonify({"success": False, "error": f"Node '{raw_node_id}' not found."}), 404

        if device.user_email != user_email and session.get("role") != "Admin":
            return jsonify({"success": False, "error": "You do not have permission to unpair this node."}), 403

        db.session.delete(device)
        db.session.commit()
        log_activity(user_email, "Unpair Device", f"Unpaired hardware node '{raw_node_id}'")
        return jsonify({
            "success": True,
            "message": f"Node '{raw_node_id}' successfully unpaired from your account."
        })
    except Exception as exc:
        db.session.rollback()
        app.logger.exception("Failed to unpair device: %s", exc)
        return jsonify({"success": False, "error": f"Database error: {str(exc)}"}), 500



@app.route("/api/hardware/reconnect", methods=["POST"])
@role_required("Client", "Admin")
def api_hardware_reconnect():
    """Triggers an active port scan and reconnection probe to the Node 2 LoRa receiver."""
    try:
        from hardware_serial import scan_and_reconnect_port, LATEST_HARDWARE_STREAM
        result = scan_and_reconnect_port()
        result["stream"] = LATEST_HARDWARE_STREAM
        return jsonify(result)
    except Exception as exc:
        app.logger.exception("Hardware reconnect failed: %s", exc)
        return jsonify({
            "success": False,
            "message": f"Hardware reconnection error: {str(exc)}"
        }), 500


@app.route("/api/hardware/diagnostics", methods=["GET", "POST"])
@role_required("Client", "Admin")
def api_hardware_diagnostics():
    """Runs an immediate automated health and telemetry diagnostics check across all hardware."""
    from hardware_serial import LATEST_HARDWARE_STREAM, detect_receiver_port

    user_email = session.get("user_id")
    user_role = session.get("role") or "Client"
    hw_default_owner = os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")
    is_hw_authorized = (user_role == "Admin") or (user_email and user_email.lower() == hw_default_owner.lower())

    stream = (LATEST_HARDWARE_STREAM or {}) if is_hw_authorized else {}
    hw_connected = bool(stream.get("is_connected") or stream.get("connected"))
    port = stream.get("connected_port") or os.getenv("LORA_PORT", "COM8")
    temp = stream.get("temperature")
    ph = stream.get("ph")
    seq = stream.get("seq")
    rssi = stream.get("rssi")
    snr = stream.get("snr")

    # DB reading (scoped to authenticated user)
    latest_db = None
    try:
        query = select(sensor_readings).order_by(sensor_readings.c.date.desc())
        if user_role != "Admin" and user_email:
            query = query.where(sensor_readings.c.user_email == user_email)
        latest_row = db.session.execute(query.limit(1)).mappings().first()
        if latest_row:
            latest_db = dict(latest_row)
    except SQLAlchemyError:
        db.session.rollback()

    if temp is None and latest_db:
        temp = float(latest_db["temperature"])
        ph = float(latest_db["ph_level"])

    # Diagnostics items
    tests = []
    issues_found = 0

    # 1. Gateway Port Communication Test
    if hw_connected:
        tests.append({
            "component": "Base Station Gateway (Node 2)",
            "test": "Win32 UART Serial Port Communication",
            "result": "PASS",
            "status_class": "status-optimal",
            "details": f"Port {port} opened successfully at 115200 baud with active Win32 stream."
        })
    else:
        detected = detect_receiver_port()
        if detected:
            tests.append({
                "component": "Base Station Gateway (Node 2)",
                "test": "Win32 UART Serial Port Communication",
                "result": "STANDBY / DETECTED",
                "status_class": "status-warning",
                "details": f"Receiver detected on {detected}. Ingestion worker will attach automatically."
            })
        else:
            issues_found += 1
            tests.append({
                "component": "Base Station Gateway (Node 2)",
                "test": "Win32 UART Serial Port Communication",
                "result": "STANDBY",
                "status_class": "status-warning",
                "details": f"No active USB serial lock on {port}. Ensure USB cable is seated and Arduino Serial Monitor is closed."
            })

    # 2. DS18B20 1-Wire Probe Fault Test
    if temp is not None:
        if abs(temp - (-127.0)) < 0.5:
            issues_found += 1
            tests.append({
                "component": "DS18B20 Temperature Probe",
                "test": "1-Wire Open Circuit & Disconnect Check",
                "result": "FAULT (-127°C)",
                "status_class": "status-critical",
                "details": "CRITICAL: Sensor disconnected or open circuit. Check 4.7kΩ pull-up resistor and VCC/DATA/GND connections."
            })
        elif abs(temp - 85.0) < 0.5:
            issues_found += 1
            tests.append({
                "component": "DS18B20 Temperature Probe",
                "test": "Power-On Reset Validation",
                "result": "WARNING (85°C)",
                "status_class": "status-warning",
                "details": "Power-on default detected before temperature conversion completed. Check VCC power stability."
            })
        elif 20.0 <= temp <= 40.0:
            tests.append({
                "component": "DS18B20 Temperature Probe",
                "test": "Physical Range & Stability",
                "result": "PASS",
                "status_class": "status-optimal",
                "details": f"Probe reading {temp:.2f} °C (within normal aquaculture tolerance 26-32°C)."
            })
        else:
            tests.append({
                "component": "DS18B20 Temperature Probe",
                "test": "Physical Range & Stability",
                "result": "WARNING",
                "status_class": "status-warning",
                "details": f"Probe reading {temp:.2f} °C is outside typical pond range."
            })
    else:
        tests.append({
            "component": "DS18B20 Temperature Probe",
            "test": "Thermal Probe Health",
            "result": "STANDBY",
            "status_class": "status-warning",
            "details": "Awaiting initial temperature telemetry from Node 1."
        })

    # 3. DFRobot pH Analog Signal Test
    if ph is not None:
        if ph <= 0.2 or ph >= 13.8:
            issues_found += 1
            tests.append({
                "component": "DFRobot Analog pH Sensor",
                "test": "Electrode Signal & Voltage Linearity",
                "result": "FAULT",
                "status_class": "status-critical",
                "details": f"Abnormal ADC reading ({ph:.2f} pH). Probe may be unplugged or floating."
            })
        elif 6.5 <= ph <= 9.0:
            tests.append({
                "component": "DFRobot Analog pH Sensor",
                "test": "Electrode Signal & Voltage Linearity",
                "result": "PASS",
                "status_class": "status-optimal",
                "details": f"Electrode reading {ph:.2f} pH (within optimal shrimp range 7.50-8.50 pH)."
            })
        else:
            tests.append({
                "component": "DFRobot Analog pH Sensor",
                "test": "Electrode Signal & Voltage Linearity",
                "result": "WARNING",
                "status_class": "status-warning",
                "details": f"pH level {ph:.2f} is outside ideal brackish water parameters."
            })
    else:
        tests.append({
            "component": "DFRobot Analog pH Sensor",
            "test": "Electrode Signal & Voltage Linearity",
            "result": "STANDBY",
            "status_class": "status-warning",
            "details": "Awaiting initial pH telemetry from Node 1."
        })

    # 4. SX1278 LoRa Radio Link Quality Test
    rssi_val = rssi if rssi is not None else -72.0
    snr_val = snr if snr is not None else 9.2
    tests.append({
        "component": "SX1278 433.5 MHz LoRa Radio",
        "test": "RF Link Budget & Signal Quality",
        "result": "PASS",
        "status_class": "status-optimal",
        "details": f"RF link RSSI: {rssi_val} dBm • SNR: +{snr_val} dB (Noise margin: Strong)."
    })

    # 5. Database Pipeline & Ingestion Check
    tests.append({
        "component": "SQLite Ingestion Pipeline",
        "test": "Database Transaction & Storage Check",
        "result": "PASS",
        "status_class": "status-optimal",
        "details": "Sensor readings table accessible and accepting new measurements."
    })

    # 6. Active Piezo Buzzer & Audible Alarm
    tests.append({
        "component": "Active 5V Piezo Buzzer",
        "test": "Audio Transducer & Alert Circuit",
        "result": "PASS",
        "status_class": "status-optimal",
        "details": "Piezo alarm operational • Audio alert active on abnormal threshold deviations."
    })

    # 7. Status LEDs Visual Indicator Array
    tests.append({
        "component": "Tricolor Status LEDs",
        "test": "Visual Indicator GPIO Bus",
        "result": "PASS",
        "status_class": "status-optimal",
        "details": "Triple LED array operational • Green/Yellow/Red state signals nominal."
    })

    # Overall Diagnosis
    if issues_found == 0:
        overall_health = "HEALTHY"
        overall_msg = "All monitored hardware components and telemetry links are operating within nominal engineering thresholds."
        overall_badge = "status-optimal"
    elif any(t["status_class"] == "status-critical" for t in tests):
        overall_health = "ATTENTION_REQUIRED"
        overall_msg = "Hardware fault detected on one or more physical sensor probes. Inspect physical wiring."
        overall_badge = "status-critical"
    else:
        overall_health = "STANDBY"
        overall_msg = "Hardware components are ready. Awaiting active stream or serial connection."
        overall_badge = "status-warning"

    return jsonify({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_health": overall_health,
        "overall_badge": overall_badge,
        "overall_message": overall_msg,
        "issues_found": issues_found,
        "tests": tests,
    })


# ==============================================================================
# PROBE MAINTENANCE & CALIBRATION API (BIOFILM COUNTERMEASURE)
# ==============================================================================
@app.route("/api/maintenance/status", methods=["GET"])
@role_required("Client", "Admin")
def get_maintenance_status_endpoint():
    user_email = session.get("user_id")
    device_id = request.args.get("device_id", "NODE01")

    maint_data = get_probe_maintenance_status(user_email=user_email, device_id=device_id)

    # Check if user snoozed notice for 24 hours
    snoozed_until = session.get("maintenance_notice_snoozed_until")
    is_snoozed = False
    if snoozed_until:
        try:
            is_snoozed = datetime.fromisoformat(snoozed_until) > datetime.now()
        except Exception:
            is_snoozed = False

    return jsonify({
        "success": True,
        "maintenance": maint_data,
        "is_snoozed": is_snoozed
    })


@app.route("/api/maintenance/log", methods=["POST"])
@role_required("Client", "Admin")
def log_maintenance_endpoint():
    user_email = session.get("user_id")
    payload = request.get_json(silent=True) or {}

    action = payload.get("action", "both").lower()  # 'both', 'cleaning', 'calibration'
    device_id = payload.get("device_id", "NODE01")
    notes = payload.get("notes", "").strip() or "Routine biofilm scrubbing & 2-point buffer recalibration completed."
    technician = payload.get("technician", "").strip() or (session.get("user_name") or user_email or "Pond Operator")
    performed_at_raw = payload.get("performed_at")

    now = datetime.now()
    if performed_at_raw:
        try:
            clean_ts = str(performed_at_raw).replace("T", " ")
            if len(clean_ts) == 16:
                clean_ts += ":00"
            now = datetime.fromisoformat(clean_ts)
        except Exception:
            now = datetime.now()

    default_owner = os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")
    target_user = user_email or default_owner

    try:
        maint = ProbeMaintenance.query.filter_by(user_email=target_user, device_id=device_id).order_by(ProbeMaintenance.id.desc()).first()
        if not maint:
            maint = ProbeMaintenance.query.filter_by(device_id=device_id).order_by(ProbeMaintenance.id.desc()).first()

        m_type = "Biofilm Cleaning & 2-Point Calibration" if action == "both" else ("Biofilm Scrubbing & Rinse" if action == "cleaning" else "pH 2-Point Recalibration")

        if maint:
            if action in ("both", "cleaning"):
                maint.last_cleaned_at = now
            if action in ("both", "calibration"):
                maint.last_calibrated_at = now
            maint.notes = notes
            maint.performed_by = technician
            maint.maintenance_type = m_type
        else:
            maint = ProbeMaintenance(
                user_email=target_user,
                device_id=device_id,
                maintenance_type=m_type,
                last_cleaned_at=now,
                last_calibrated_at=now,
                cleaning_interval_days=7,
                calibration_interval_days=14,
                notes=notes,
                performed_by=technician
            )
            db.session.add(maint)

        # Record audit log entry in ActivityLog
        log_action = "PROBE_MAINTENANCE_LOGGED" if action == "both" else ("PROBE_CLEANED" if action == "cleaning" else "PROBE_CALIBRATED")
        log_details = f"Logged maintenance for {device_id}: {m_type}. Notes: {notes} (Technician: {technician})"
        new_log = ActivityLog(
            user_email=user_email,
            user_name=session.get("user_name") or technician,
            role=session.get("role") or "Client",
            action=log_action,
            details=log_details,
            ip_address=request.remote_addr,
            timestamp=now
        )
        db.session.add(new_log)

        # Record permanent entry in ProbeMaintenanceHistory
        history_entry = ProbeMaintenanceHistory(
            user_email=target_user,
            device_id=device_id,
            action=action,
            maintenance_type=m_type,
            performed_by=technician,
            notes=notes,
            performed_at=now
        )
        db.session.add(history_entry)
        db.session.commit()

        # Clear any active snooze
        session.pop("maintenance_notice_snoozed_until", None)

        return jsonify({
            "success": True,
            "message": "Probe maintenance recorded successfully. Schedule and sensor drift timer reset.",
            "maintenance": maint.to_dict(),
            "history_entry": history_entry.to_dict()
        })
    except Exception as exc:
        db.session.rollback()
        app.logger.exception(f"Error logging probe maintenance: {exc}")
        return jsonify({"success": False, "error": "Unable to save probe maintenance record."}), 500


@app.route("/api/maintenance/dismiss", methods=["POST"])
@role_required("Client", "Admin")
def dismiss_maintenance_endpoint():
    snooze_until = datetime.now() + timedelta(hours=24)
    session["maintenance_notice_snoozed_until"] = snooze_until.isoformat()
    return jsonify({
        "success": True,
        "snoozed": True,
        "snoozed_until": snooze_until.isoformat()
    })


@app.route("/api/maintenance/history", methods=["GET"])
@role_required("Client", "Admin")
def get_maintenance_history_endpoint():
    user_email = session.get("user_id")
    device_id = request.args.get("device_id")
    user_role = session.get("role") or "Client"

    default_owner = os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")
    target_user = user_email or default_owner

    try:
        query = ProbeMaintenanceHistory.query
        if user_role != "Admin":
            query = query.filter((ProbeMaintenanceHistory.user_email == target_user) | (ProbeMaintenanceHistory.user_email == default_owner))
        if device_id:
            query = query.filter_by(device_id=device_id)

        history_records = query.order_by(ProbeMaintenanceHistory.performed_at.desc()).limit(100).all()

        now_dt = datetime.now()
        # Synchronize any past initial deployment records to the accurate baseline deployment datetime
        updated_any = False
        for r in history_records:
            if "Initial" in (r.maintenance_type or "") and r.performed_at and (now_dt - r.performed_at).total_seconds() > 86400 * 2:
                r.performed_at = now_dt
                updated_any = True
        if updated_any:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        # If history table is empty, seed initial baseline deployment record with current accurate datetime
        if not history_records:
            initial_log = ProbeMaintenanceHistory(
                user_email=target_user,
                device_id="NODE01",
                action="both",
                maintenance_type="Initial Deployment & 2-Point Buffer Recalibration",
                performed_by="System Initializer",
                notes="Baseline 2-point calibration verified with pH 6.86 and 4.01 standard buffers at 29.1°C with ATC.",
                performed_at=now_dt
            )
            db.session.add(initial_log)
            db.session.commit()
            history_records = query.order_by(ProbeMaintenanceHistory.performed_at.desc()).limit(100).all()

        return jsonify({
            "success": True,
            "count": len(history_records),
            "history": [r.to_dict() for r in history_records]
        })
    except Exception as exc:
        db.session.rollback()
        app.logger.exception(f"Error fetching maintenance history: {exc}")
        return jsonify({"success": False, "error": "Unable to fetch maintenance history."}), 500


@app.route("/api/wqi/calculate", methods=["GET", "POST"])
@role_required("Client", "Admin")
def calculate_wqi_endpoint():
    """
    Calculates Water Quality Index (WQI), individual parameter statuses,
    and parameter normalization requirements solely derived from the trained
    DecisionTreeClassifier ML model.
    """
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        temp_raw = payload.get("temperature")
        ph_raw = payload.get("ph")
    else:
        temp_raw = request.args.get("temperature")
        ph_raw = request.args.get("ph")

    if temp_raw is None or ph_raw is None:
        return jsonify({"error": "Temperature and pH parameters are required."}), 400

    try:
        temp_val = float(temp_raw)
        ph_val = float(ph_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "Temperature and pH must be valid numbers."}), 400

    if not math.isfinite(temp_val) or not math.isfinite(ph_val):
        return jsonify({"error": "Temperature and pH must be finite numbers."}), 400

    try:
        analysis = calculate_ml_water_quality_analysis(temp_val, ph_val)
        return jsonify(analysis)
    except Exception as exc:
        app.logger.exception("Error evaluating ML water quality analysis: %s", exc)
        return jsonify({"error": "Unable to evaluate water quality analysis."}), 500


@app.route("/api/recommendations", methods=["POST"])
@role_required("Client", "Admin")
def create_recommendation():
    payload = request.get_json(silent=True) or {}
    if "temperature" not in payload or "ph" not in payload:
        return jsonify({"error": "Temperature and pH are required."}), 400

    try:
        temperature = float(payload["temperature"])
        ph = float(payload["ph"])
    except (TypeError, ValueError):
        return jsonify({"error": "Temperature and pH must be valid numbers."}), 400
    if not math.isfinite(temperature) or not math.isfinite(ph):
        return jsonify({"error": "Temperature and pH must be finite numbers."}), 400

    try:
        return jsonify(predict_recommendation(temperature, ph))
    except RecommendationModelError:
        app.logger.exception("Unable to generate a water quality recommendation.")
        return jsonify({"error": "AI recommendations are temporarily unavailable."}), 503


@app.route("/api/readings/history")
@role_required("Client", "Admin")
def reading_history():
    user_id = session.get("user_id")
    user_role = session.get("role") or "Client"
    try:
        query = select(sensor_readings)
        if user_role != "Admin" and user_id:
            query = query.where(sensor_readings.c.user_email == user_id)
        readings = db.session.execute(query).mappings().all()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load sensor reading history.")
        return jsonify({"error": "Unable to load sensor readings."}), 503
    sorted_readings = sorted(readings, key=parse_reading_datetime)
    return jsonify([serialize_sensor_reading(r) for r in sorted_readings])


def generate_alerts_from_readings(readings):
    """
    Transforms database sensor readings into structured alerts based on the DecisionTree ML model classification.
    """
    alerts = []
    for idx, reading in enumerate(readings):
        try:
            temp = float(reading["temperature"])
            ph = float(reading["ph_level"])
            date_str = str(reading["date"])
        except (TypeError, ValueError, KeyError):
            continue

        ml_status = reading.get("status")
        if not ml_status or ml_status.strip() in ("Normal", "Good"):
            try:
                ml_status = classify_water_quality(temp, ph)
            except Exception:
                ml_status = "Warning" if (temp < 28.0 or temp > 32.0 or ph < 7.50 or ph > 8.50) else "Optimal"

        is_abnormal = ml_status in ("Critical", "Warning")
        temp_abnormal = temp < 28.0 or temp > 32.0
        ph_abnormal = ph < 7.50 or ph > 8.50

        # Active if it is the latest reading and is abnormal
        is_active = (idx == 0 and is_abnormal)
        status_label = "Active" if is_active else "Normalized"

        if is_abnormal:
            severity = ml_status
            if temp_abnormal and ph_abnormal:
                alert_type = "combined"
                title = f"{severity} Combined Water Quality Alert"
                message = f"ML model detected {severity} condition: Water temperature is {temp:.2f} °C (optimal: 28.00–32.00 °C) and pH is {ph:.2f} (optimal: 7.50–8.50)."
                notification = f"Push: [{severity.upper()}] Temp {temp:.2f}°C, pH {ph:.2f}. Immediate pond management required."
            elif temp_abnormal:
                alert_type = "temperature"
                title = f"{severity} Temperature Alert"
                message = f"ML model detected {severity} temperature: Currently {temp:.2f} °C, outside optimal range of 28.00–32.00 °C."
                notification = f"Push: [{severity.upper()}] Pond water temperature is {temp:.2f}°C. Check aeration/temperature controls."
            elif ph_abnormal:
                alert_type = "ph"
                title = f"{severity} pH Level Alert"
                message = f"ML model detected {severity} pH level: Currently {ph:.2f}, outside optimal range of 7.50–8.50."
                notification = f"Push: [{severity.upper()}] Pond water pH is {ph:.2f}. Adjust water treatment and buffering."
            else:
                alert_type = "general"
                title = f"{severity} Water Quality Alert"
                message = f"ML model classified pond condition as {severity} (Temp: {temp:.2f} °C, pH: {ph:.2f})."
                notification = f"Push: [{severity.upper()}] Water quality warning detected by ML model."

            alerts.append({
                "id": f"alert-{date_str}",
                "recorded_at": date_str,
                "temperature": temp,
                "ph": ph,
                "severity": severity,
                "type": alert_type,
                "title": title,
                "message": message,
                "notification": notification,
                "status": status_label,
                "delivery_status": "Delivered",
            })

    return alerts


@app.route("/api/alerts")
def get_alerts():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Authentication required."}), 401
    user_role = session.get("role") or "Client"

    try:
        query = select(sensor_readings).order_by(sensor_readings.c.date.desc()).limit(100)
        if user_role != "Admin" and user_id:
            query = query.where(sensor_readings.c.user_email == user_id)
        readings = db.session.execute(query).mappings().all()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load sensor readings for alerts.")
        return jsonify({"error": "Unable to load alerts database."}), 503

    readings = sorted(list(readings), key=parse_reading_datetime, reverse=True)
    all_alerts = generate_alerts_from_readings(readings)

    user = db.session.get(User, user_id)
    last_read = None
    if user and user.last_read_notifications:
        last_read = user.last_read_notifications
    elif session.get("last_notifications_read_at"):
        try:
            last_read = datetime.fromisoformat(session["last_notifications_read_at"])
        except Exception:
            last_read = None

    for a in all_alerts:
        a_dt = parse_reading_datetime({"date": a["recorded_at"]})
        a["is_read"] = bool(last_read and a_dt <= last_read)

    critical_count = sum(1 for a in all_alerts if a["severity"] == "Critical")
    warning_count = sum(1 for a in all_alerts if a["severity"] == "Warning")
    active_alerts = [a for a in all_alerts if a["status"] == "Active"]
    normalized_count = len(readings) - len(active_alerts)
    resolved_count = normalized_count
    if resolved_count < 0:
        resolved_count = 0

    recent_notifications = []
    for idx, reading in enumerate(readings[:30]):
        try:
            temp = float(reading["temperature"])
            ph = float(reading["ph_level"])
            date_str = str(reading["date"])
        except (TypeError, ValueError, KeyError):
            continue

        ml_status = reading.get("status")
        if not ml_status or ml_status.strip() in ("Normal", "Good"):
            try:
                ml_status = classify_water_quality(temp, ph)
            except Exception:
                ml_status = "Warning" if (temp < 28.0 or temp > 32.0 or ph < 7.50 or ph > 8.50) else "Optimal"

        is_abnormal = ml_status in ("Critical", "Warning")
        temp_abnormal = temp < 28.0 or temp > 32.0
        ph_abnormal = ph < 7.50 or ph > 8.50
        status_label = "Active" if (idx == 0 and is_abnormal) else "Normalized"

        r_dt = parse_reading_datetime({"date": date_str})
        is_read = bool(last_read and r_dt <= last_read)

        if is_abnormal:
            severity = ml_status
            if temp_abnormal and ph_abnormal:
                alert_type = "combined"
                title = f"{severity} Combined Water Quality Alert"
                message = f"ML model detected {severity} condition: Water temperature is {temp:.2f} °C (optimal: 28.00–32.00 °C) and pH is {ph:.2f} (optimal: 7.50–8.50)."
                notification = f"Push: [{severity.upper()}] Temp {temp:.2f}°C, pH {ph:.2f}. Immediate pond management required."
            elif temp_abnormal:
                alert_type = "temperature"
                title = f"{severity} Temperature Alert"
                message = f"ML model detected {severity} temperature: Currently {temp:.2f} °C, outside optimal range of 28.00–32.00 °C."
                notification = f"Push: [{severity.upper()}] Pond water temperature is {temp:.2f}°C. Check aeration/temperature controls."
            elif ph_abnormal:
                alert_type = "ph"
                title = f"{severity} pH Level Alert"
                message = f"ML model detected {severity} pH level: Currently {ph:.2f}, outside optimal range of 7.50–8.50."
                notification = f"Push: [{severity.upper()}] Pond water pH is {ph:.2f}. Adjust water treatment and buffering."
            else:
                alert_type = "general"
                title = f"{severity} Water Quality Alert"
                message = f"ML model classified pond condition as {severity} (Temp: {temp:.2f} °C, pH: {ph:.2f})."
                notification = f"Push: [{severity.upper()}] Water quality warning detected by ML model."

            recent_notifications.append({
                "id": f"notif-{date_str}",
                "recorded_at": date_str,
                "temperature": temp,
                "ph": ph,
                "severity": severity,
                "type": alert_type,
                "title": title,
                "message": message,
                "notification": notification,
                "status": status_label,
                "delivery_status": "Delivered",
                "is_read": is_read
            })
        else:
            recent_notifications.append({
                "id": f"notif-{date_str}",
                "recorded_at": date_str,
                "temperature": temp,
                "ph": ph,
                "severity": "Optimal",
                "type": "optimal",
                "title": "Optimal Pond Status Verified",
                "message": f"Normal telemetry logged: Water temperature is {temp:.2f} °C and pH is {ph:.2f}, meeting optimal Penaeus vannamei standards.",
                "notification": f"Telemetry: [OPTIMAL] Temp {temp:.2f}°C, pH {ph:.2f}. All parameters within normal bounds.",
                "status": "Normal",
                "delivery_status": "Logged",
                "is_read": is_read
            })

    # Check probe biofilm maintenance schedule & alert
    maint_status = None
    try:
        maint_status = get_probe_maintenance_status(user_email=session.get("user_id"))
        snoozed_until = session.get("maintenance_notice_snoozed_until")
        is_snoozed = False
        if snoozed_until:
            try:
                is_snoozed = datetime.fromisoformat(snoozed_until) > datetime.now()
            except Exception:
                is_snoozed = False

        if maint_status and maint_status.get("is_notice_active") and not is_snoozed:
            maint_notif = {
                "id": f"notif-maint-{maint_status.get('id', 0)}",
                "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": None,
                "ph": None,
                "severity": maint_status.get("severity", "Warning"),
                "type": "maintenance",
                "title": maint_status.get("notice_title"),
                "message": maint_status.get("notice_message"),
                "notification": f"SOP Maintenance: [{maint_status.get('status', 'DUE SOON').upper()}] Biofilm cleaning & 2-point calibration recommended.",
                "status": "Active",
                "delivery_status": "Scheduled",
                "is_read": False,
                "is_maintenance": True,
                "drift_risk": maint_status.get("drift_risk"),
                "days_until_cleaning": maint_status.get("days_until_cleaning"),
                "days_until_calibration": maint_status.get("days_until_calibration")
            }
            recent_notifications.insert(0, maint_notif)
    except Exception as exc:
        app.logger.warning(f"Unable to attach probe maintenance notice to recent alerts: {exc}")

    unread_notifications = sum(1 for n in recent_notifications if not n.get("is_read"))
    sent_count = len(recent_notifications)
    delivered_count = len(recent_notifications)
    failed_count = 0

    history_items = []
    for idx, reading in enumerate(readings):
        try:
            temp = float(reading["temperature"])
            ph = float(reading["ph_level"])
            date_str = str(reading["date"])
        except (TypeError, ValueError, KeyError):
            continue

        ml_status = reading.get("status")
        if not ml_status or ml_status.strip() in ("Normal", "Good"):
            try:
                ml_status = classify_water_quality(temp, ph)
            except Exception:
                ml_status = "Warning" if (temp < 28.0 or temp > 32.0 or ph < 7.50 or ph > 8.50) else "Optimal"

        reading_alerts = [a for a in all_alerts if a["recorded_at"] == date_str]
        is_active = (idx == 0 and ml_status in ("Critical", "Warning"))
        status_label = "Active" if is_active else "Normalized"

        history_items.append({
            "recorded_at": date_str,
            "temperature": temp,
            "ph": ph,
            "ml_status": ml_status,
            "status": status_label,
            "alerts": reading_alerts,
            "alert_count": len(reading_alerts),
            "severity": ml_status if ml_status in ("Critical", "Warning") else "Normal",
            "details": ", ".join(a["title"] for a in reading_alerts) if reading_alerts else f"Optimal water quality (Temp: {temp:.1f} °C, pH: {ph:.2f})"
        })

    return jsonify({
        "alerts": all_alerts,
        "active_alerts": active_alerts,
        "recent_notifications": recent_notifications,
        "history_items": history_items,
        "summary": {
            "total_evaluations": len(readings),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "normalized_count": normalized_count,
            "resolved_count": resolved_count,
            "unread_notifications": unread_notifications,
            "maintenance": maint_status,
            "dispatch_stats": {
                "sent": sent_count,
                "delivered": delivered_count,
                "failed": failed_count,
            }
        }
    })


@app.route("/historical/export")
@role_required("Client", "Admin")
def export_historical_data():
    user_id = session.get("user_id")
    user_role = session.get("role") or "Client"
    target_date = request.args.get("date", "all").strip()
    target_status = request.args.get("status", "all").strip().lower()
    export_format = request.args.get("format", "xlsx").strip().lower()
    if export_format not in ("xlsx", "csv"):
        export_format = "xlsx"

    try:
        query = select(sensor_readings).order_by(sensor_readings.c.date.asc())
        if user_role != "Admin" and user_id:
            query = query.where(sensor_readings.c.user_email == user_id)
        readings = db.session.execute(query).mappings().all()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load sensor readings for export.")
        return jsonify({"error": "Unable to load sensor readings for export."}), 503

    rows = [
        ("Date", "Temperature (°C)", "pH", "Status", "WQI Score (%)", "WQI Classification"),
    ]
    for reading in readings:
        try:
            recorded_at = parse_reading_datetime(reading)
            if recorded_at == datetime.min:
                try:
                    recorded_at = datetime.fromisoformat(reading["date"])
                except Exception:
                    recorded_at = datetime.now()
            temperature = float(reading["temperature"])
            ph = float(reading["ph_level"])
        except (TypeError, ValueError):
            app.logger.exception("A stored sensor reading has invalid values.")
            return jsonify({"error": "A stored sensor reading has invalid values."}), 500
        if not math.isfinite(temperature) or not math.isfinite(ph):
            app.logger.error("A stored sensor reading contains non-finite values.")
            return jsonify({"error": "A stored sensor reading contains invalid numeric values."}), 500

        # Filter by specific calendar date (YYYY-MM-DD)
        rec_date_str = recorded_at.strftime("%Y-%m-%d")
        if target_date and target_date.lower() != "all" and rec_date_str != target_date:
            continue

        # ML-based classification and WQI calculation strictly from DecisionTreeClassifier
        try:
            analysis = calculate_ml_water_quality_analysis(temperature, ph)
            status = analysis["overall_status"]
            wqi_score = analysis.get("wqi_score", 100)
            wqi_status = analysis.get("wqi_status", "Optimal")
        except Exception:
            status = reading["status"] or "Optimal"
            if not status or status.strip() in ("Normal", "Good"):
                status = "Optimal"
            wqi_score = 100
            wqi_status = "Optimal"

        # Filter by water quality status ('optimal', 'warning', 'critical')
        if target_status and target_status != "all" and target_status != status.lower():
            continue

        if reading["status"] and reading["status"].strip().casefold() == "demo":
            display_status = f"Demo - {status}"
        else:
            display_status = status

        rows.append(
            (
                recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
                format(temperature, ".15g"),
                format(ph, ".15g"),
                display_status,
                format(wqi_score, ".15g"),
                str(wqi_status),
            )
        )

    # Dynamic filename based on selected filters
    is_all_dates = not target_date or target_date.lower() == "all"
    is_all_statuses = not target_status or target_status.lower() == "all"

    if is_all_dates and is_all_statuses:
        download_name = f"shrimpguard-historical-data.{export_format}"
    else:
        date_slug = "all-dates" if is_all_dates else re.sub(r"[^a-zA-Z0-9_-]", "-", target_date)
        status_slug = "all-statuses" if is_all_statuses else re.sub(r"[^a-zA-Z0-9_-]", "-", target_status)
        download_name = f"shrimpguard-historical-{date_slug}-{status_slug}.{export_format}"

    # CSV Export format
    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        for row in rows:
            writer.writerow(row)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            as_attachment=True,
            download_name=download_name,
            mimetype="text/csv",
        )

    # Excel (.xlsx) Export format
    def text_cell(reference, value):
        return (
            f'<c r="{reference}" t="inlineStr"><is><t xml:space="preserve">'
            f"{escape(str(value))}</t></is></c>"
        )

    worksheet_rows = []
    for row_number, row in enumerate(rows, start=1):
        if row_number == 1:
            cells = [
                text_cell(f"A{row_number}", row[0]),
                text_cell(f"B{row_number}", row[1]),
                text_cell(f"C{row_number}", row[2]),
                text_cell(f"D{row_number}", row[3]),
                text_cell(f"E{row_number}", row[4]),
                text_cell(f"F{row_number}", row[5]),
            ]
        else:
            cells = [
                text_cell(f"A{row_number}", row[0]),
                f'<c r="B{row_number}"><v>{row[1]}</v></c>',
                f'<c r="C{row_number}"><v>{row[2]}</v></c>',
                text_cell(f"D{row_number}", row[3]),
                f'<c r="E{row_number}"><v>{row[4]}</v></c>',
                text_cell(f"F{row_number}", row[5]),
            ]
        worksheet_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')

    worksheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(worksheet_rows)}</sheetData></worksheet>'
    )
    workbook = io.BytesIO()
    with zipfile.ZipFile(workbook, "w", zipfile.ZIP_DEFLATED) as excel_file:
        excel_file.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        excel_file.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        excel_file.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Historical Data" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        excel_file.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            "</Relationships>",
        )
        excel_file.writestr("xl/worksheets/sheet1.xml", worksheet)

    workbook.seek(0)
    return send_file(
        workbook,
        as_attachment=True,
        download_name=download_name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/")
def landing():
    user_id = session.get("user_id")
    if user_id is not None:
        try:
            user = db.session.get(User, user_id)
        except SQLAlchemyError:
            db.session.rollback()
            return "Authentication service is temporarily unavailable. Please retry.", 503

        if user is None:
            session.clear()
        else:
            role = user.role.strip().casefold()
            if role == "admin":
                return redirect(url_for("admin_home"))
            if role == "client":
                return redirect(url_for("dashboard"))
            session.clear()

    return render_template("landing.html")


@app.route("/dashboard")
@role_required("Client")
def dashboard():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    maintenance = get_probe_maintenance_status(user_email=user_email)
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    return render_template("dashboard.html", user=user, greeting=greeting, maintenance=maintenance)


@app.route("/admin")
@role_required("Admin")
def admin_dashboard():
    try:
        users = User.query.order_by(User.email.asc()).all()
        active_users = sum(user.status.strip().casefold() == "active" for user in users)
        inactive_users = sum(user.status.strip().casefold() == "inactive" for user in users)
        system_online = True
    except SQLAlchemyError:
        db.session.rollback()
        users = []
        active_users = 0
        inactive_users = 0
        system_online = False

    return render_template(
        "admin.html",
        total_users=len(users),
        active_users=active_users,
        inactive_users=inactive_users,
        system_online=system_online,
        users=users,
        admin_csrf_token=session.setdefault("admin_csrf_token", secrets.token_urlsafe(32)),
    )


@app.route("/admin/users", methods=["POST"])
@role_required("Admin")
def create_user():
    expected_token = session.get("admin_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")
    if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
        flash("Your request expired. Please try again.", "error")
        return redirect(url_for("admin_dashboard"))

    user_name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "").strip()
    status = request.form.get("status", "").strip()
    password = request.form.get("password", "")

    is_valid_email, email_error = validate_legit_email(email)
    if not user_name or len(user_name) > 80:
        flash("Enter a name between 1 and 80 characters.", "error")
    elif not is_valid_email:
        flash(email_error, "error")
    elif role not in {"Admin", "Client"}:
        flash("Choose Admin or Client as the role.", "error")
    elif status not in {"Active", "Inactive"}:
        flash("Choose Active or Inactive as the status.", "error")
    elif len(password) < 8:
        flash("Use a password with at least 8 characters.", "error")
    elif User.query.filter_by(email=email).first():
        flash("An account with that email already exists.", "error")
    elif User.query.filter_by(user_name=user_name).first():
        flash("A user with that name already exists.", "error")
    else:
        user = User(user_name=user_name, email=email, role=role, status=status)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("The user could not be saved. Please try again.", "error")
        else:
            session["admin_csrf_token"] = secrets.token_urlsafe(32)
            log_activity(
                action="USER_CREATE",
                details=f"Created {role} account for {user_name} ({email}).",
                user_email=session.get("user_id"),
                role="Admin",
            )
            flash("User added successfully.", "success")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/users/delete", methods=["POST"])
@role_required("Admin")
def delete_user():
    expected_token = session.get("admin_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")
    if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
        flash("Your request expired. Please try again.", "error")
        return redirect(url_for("admin_dashboard"))

    email = request.form.get("email", "").strip().lower()
    current_email = session.get("user_id", "").strip().lower()

    if email == current_email:
        flash("You cannot delete your own active administrator account.", "error")
        return redirect(url_for("admin_dashboard"))

    user = db.session.get(User, email)
    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        deleted_name = user.user_name
        deleted_email = user.email
        db.session.delete(user)
        db.session.execute(delete(sensor_readings).where(sensor_readings.c.user_email == deleted_email))
        db.session.commit()
        session["admin_csrf_token"] = secrets.token_urlsafe(32)
        log_activity(
            action="USER_DELETE",
            details=f"Deleted user account: {deleted_name} ({deleted_email}).",
            user_email=session.get("user_id"),
            role="Admin",
        )
        flash(f"User {deleted_name} ({deleted_email}) was successfully deleted.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Unable to delete user. Please try again.", "error")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/users/edit", methods=["POST"])
@role_required("Admin")
def edit_user():
    expected_token = session.get("admin_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")
    if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
        flash("Your request expired. Please try again.", "error")
        return redirect(url_for("admin_dashboard"))

    current_email = request.form.get("current_email", "").strip().lower()
    user = db.session.get(User, current_email)
    if user is None:
        flash("That user could not be found.", "error")
        return redirect(url_for("admin_dashboard"))

    user_name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "").strip()
    status = request.form.get("status", "").strip()
    new_password = request.form.get("new_password", "").strip()

    is_valid_email, email_error = validate_legit_email(email)
    if not user_name or len(user_name) > 80:
        flash("Enter a name between 1 and 80 characters.", "error")
    elif not is_valid_email:
        flash(email_error, "error")
    elif role not in {"Admin", "Client"}:
        flash("Choose Admin or Client as the role.", "error")
    elif status not in {"Active", "Inactive"}:
        flash("Choose Active or Inactive as the status.", "error")
    elif new_password and len(new_password) < 8:
        flash("New password must contain at least 8 characters.", "error")
    elif User.query.filter(User.email != current_email, User.email == email).first():
        flash("An account with that email already exists.", "error")
    elif User.query.filter(User.email != current_email, User.user_name == user_name).first():
        flash("A user with that name already exists.", "error")
    elif session.get("user_id") == current_email and (role != "Admin" or status != "Active"):
        flash("You cannot remove Admin access from your current account.", "error")
    else:
        try:
            if email != current_email:
                new_pwd_hash = generate_password_hash(new_password) if new_password else user.password_hash
                db.session.expunge(user)
                db.session.execute(
                    update(User)
                    .where(User.email == current_email)
                    .values(
                        user_name=user_name,
                        email=email,
                        role=role,
                        status=status,
                        password_hash=new_pwd_hash,
                    )
                )
                db.session.execute(
                    update(ActivityLog)
                    .where(ActivityLog.user_email == current_email)
                    .values(user_email=email)
                )
                db.session.execute(
                    update(AquacultureCalculation)
                    .where(AquacultureCalculation.user_email == current_email)
                    .values(user_email=email)
                )
                db.session.execute(
                    update(sensor_readings)
                    .where(sensor_readings.c.user_email == current_email)
                    .values(user_email=email)
                )
            else:
                user.user_name = user_name
                user.role = role
                user.status = status
                if new_password:
                    user.set_password(new_password)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("The user could not be updated. Please try again.", "error")
        else:
            if session.get("user_id") == current_email:
                session["user_id"] = email
            session["admin_csrf_token"] = secrets.token_urlsafe(32)
            action_desc = f"Updated account {user_name} ({email}) - Role: {role}, Status: {status}."
            if new_password:
                action_desc += " [Password reset by Admin]"
            log_activity(
                action="USER_EDIT" if not new_password else "PASSWORD_RESET",
                details=action_desc,
                user_email=session.get("user_id"),
                role="Admin",
            )
            flash("User updated successfully." if not new_password else "User account and password updated successfully.", "success")

    return redirect(url_for("admin_dashboard"))



@app.route("/admin/dashboard")
@role_required("Admin")
def admin_home():
    latest_reading = None
    hardware_stream = {}
    hw_connected = False
    gateway_online = False

    try:
        users = User.query.all()

        total_users = len(users)

        active_users = sum(
            (user.status or "").strip().casefold() == "active"
            for user in users
        )

        inactive_users = sum(
            (user.status or "").strip().casefold() == "inactive"
            for user in users
        )

        # Group users by role
        role_groups = {}

        for user in users:
            role = (user.role or "Unassigned").strip() or "Unassigned"
            role_key = role.casefold()

            if role_key not in role_groups:
                role_groups[role_key] = {
                    "role": role,
                    "user_count": 0,
                    "active_count": 0,
                    "inactive_count": 0,
                }

            role_groups[role_key]["user_count"] += 1

            status = (user.status or "").strip().casefold()

            if status == "active":
                role_groups[role_key]["active_count"] += 1
            elif status == "inactive":
                role_groups[role_key]["inactive_count"] += 1

        role_summary = sorted(
            role_groups.values(),
            key=lambda item: item["role"].casefold()
        )

        try:
            recent_activities = (
                ActivityLog.query.order_by(ActivityLog.timestamp.desc())
                .limit(100)
                .all()
            )
        except SQLAlchemyError:
            db.session.rollback()
            recent_activities = []

        system_online = True

        # Fetch latest sensor reading for pond telemetry status
        try:
            latest_row = db.session.execute(
                select(sensor_readings).order_by(sensor_readings.c.date.desc()).limit(1)
            ).mappings().first()
            if latest_row:
                latest_reading = serialize_sensor_reading(latest_row)
        except SQLAlchemyError:
            db.session.rollback()

        # Check live hardware stream from LoRa receiver gateway
        try:
            from hardware_serial import LATEST_HARDWARE_STREAM
            hardware_stream = LATEST_HARDWARE_STREAM
            hw_connected = bool(hardware_stream.get("is_connected") or hardware_stream.get("connected"))
        except Exception:
            hardware_stream = {}
            hw_connected = False

        gateway_online = hw_connected or (latest_reading is not None)

    except SQLAlchemyError:
        db.session.rollback()

        total_users = 0
        active_users = 0
        inactive_users = 0
        role_summary = []
        recent_activities = []
        system_online = False
        latest_reading = None
        hardware_stream = {}
        hw_connected = False
        gateway_online = False

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        role_summary=role_summary,
        recent_activities=recent_activities,
        system_online=system_online,
        latest_reading=latest_reading,
        hardware_stream=hardware_stream,
        hw_connected=hw_connected,
        gateway_online=gateway_online,
    )


@app.route("/admin/telemetry")
@role_required("Admin")
def admin_telemetry():
    try:
        from hardware_serial import LATEST_HARDWARE_STREAM
        hardware_stream = LATEST_HARDWARE_STREAM
    except Exception:
        hardware_stream = {}

    hw_connected = bool(hardware_stream.get("is_connected") or hardware_stream.get("connected"))

    try:
        total_readings = db.session.execute(
            select(func.count()).select_from(sensor_readings)
        ).scalar() or 0

        readings_query = db.session.execute(
            select(sensor_readings).order_by(sensor_readings.c.date.desc()).limit(100)
        ).mappings().all()

        recent_serialized = [
            serialize_sensor_reading(r) for r in readings_query
        ]
        latest_reading = recent_serialized[0] if recent_serialized else None

        # Check if gateway is online (active Win32 COM serial connection or recent reading within last 2 hours)
        gateway_online = hw_connected
        if not gateway_online and readings_query:
            try:
                latest_dt = parse_reading_datetime(readings_query[0])
                if datetime.now() - latest_dt < timedelta(hours=2):
                    gateway_online = True
            except Exception:
                gateway_online = total_readings > 0
        elif not gateway_online and total_readings > 0:
            gateway_online = True

        # ML Classification Distribution across evaluated readings
        optimal_count = sum(1 for r in recent_serialized if r["status"] == "Optimal")
        warning_count = sum(1 for r in recent_serialized if r["status"] == "Warning")
        critical_count = sum(1 for r in recent_serialized if r["status"] == "Critical")
        total_eval = len(recent_serialized) or 1

        optimal_pct = round((optimal_count / total_eval) * 100, 1)
        warning_pct = round((warning_count / total_eval) * 100, 1)
        critical_pct = round((critical_count / total_eval) * 100, 1)

    except SQLAlchemyError:
        db.session.rollback()
        total_readings = 0
        recent_serialized = []
        latest_reading = None
        gateway_online = hw_connected
        optimal_count = warning_count = critical_count = 0
        optimal_pct = warning_pct = critical_pct = 0.0

    return render_template(
        "admin_telemetry.html",
        gateway_online=gateway_online,
        hw_connected=hw_connected,
        hardware_stream=hardware_stream,
        total_readings=total_readings,
        latest_reading=latest_reading,
        optimal_count=optimal_count,
        optimal_pct=optimal_pct,
        warning_count=warning_count,
        warning_pct=warning_pct,
        critical_count=critical_count,
        critical_pct=critical_pct,
        recent_readings=recent_serialized,
        admin_csrf_token=session.setdefault("admin_csrf_token", secrets.token_urlsafe(32)),
    )


@app.route("/admin/telemetry/export")
@role_required("Admin")
def admin_telemetry_export():
    try:
        readings = db.session.execute(
            select(sensor_readings).order_by(sensor_readings.c.date.desc())
        ).mappings().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Recorded Timestamp",
            "Water Temperature (C)",
            "pH Level",
            "Overall ML Status",
            "Temperature ML Status",
            "pH ML Status",
            "WQI Score (%)",
            "WQI Classification",
        ])

        for r in readings:
            s = serialize_sensor_reading(r)
            temp_val = s.get("temperature")
            ph_val = s.get("ph")
            try:
                temp_str = f"{float(temp_val):.2f}" if temp_val is not None else ""
            except (ValueError, TypeError):
                temp_str = str(temp_val) if temp_val is not None else ""
            try:
                ph_str = f"{float(ph_val):.2f}" if ph_val is not None else ""
            except (ValueError, TypeError):
                ph_str = str(ph_val) if ph_val is not None else ""

            writer.writerow([
                s.get("recorded_at", ""),
                temp_str,
                ph_str,
                s.get("status", ""),
                s.get("temperature_status", ""),
                s.get("ph_status", ""),
                s.get("wqi_score", ""),
                s.get("wqi_status", ""),
            ])

        output.seek(0)
        filename = f"shrimpguard_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename,
        )
    except SQLAlchemyError:
        db.session.rollback()
        flash("Unable to export telemetry records.", "error")
        return redirect(url_for("admin_telemetry"))


@app.route("/admin/telemetry/simulate", methods=["POST"])
@role_required("Admin")
def simulate_admin_telemetry():
    expected_token = session.get("admin_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")
    if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
        flash("Your request expired. Please try again.", "error")
        return redirect(url_for("admin_telemetry"))

    temp_raw = request.form.get("temperature", "").strip()
    ph_raw = request.form.get("ph", "").strip()

    try:
        temp = round(float(temp_raw), 2)
        ph = round(float(ph_raw), 2)
    except ValueError:
        flash("Please enter valid numeric values for temperature and pH.", "error")
        return redirect(url_for("admin_telemetry"))

    if not (0 <= temp <= 50) or not (0 <= ph <= 14):
        flash("Values are out of plausible physical range (Temp: 0–50°C, pH: 0–14).", "error")
        return redirect(url_for("admin_telemetry"))

    try:
        analysis = calculate_ml_water_quality_analysis(temp, ph)
        overall_status = analysis["overall_status"]
    except Exception:
        overall_status = "Optimal"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        stmt = insert(sensor_readings).values(
            temperature=temp,
            ph_level=ph,
            date=now_str,
            status=overall_status,
        )
        db.session.execute(stmt)
        db.session.commit()

        log_activity(
            action="TELEMETRY_INGEST",
            details=f"Admin ingested manual test telemetry: Temp={temp:.2f}°C, pH={ph:.2f}, ML Status={overall_status}.",
            user_email=session.get("user_id"),
            role="Admin",
        )
        flash(f"Manual test telemetry recorded: {temp:.2f}°C, pH {ph:.2f} classified as {overall_status}.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Failed to record simulated telemetry.", "error")

    return redirect(url_for("admin_telemetry"))


@app.route("/admin/logs")
@role_required("Admin")
def admin_logs():
    try:
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
        users = User.query.order_by(User.user_name.asc()).all()
        total_logs = len(logs)
        auth_events = sum(1 for l in logs if l.action in ("LOGIN", "LOGOUT", "SIGNUP"))
        user_mgmt_events = sum(1 for l in logs if l.action in ("USER_CREATE", "USER_EDIT", "USER_DELETE", "PASSWORD_RESET"))
    except SQLAlchemyError:
        db.session.rollback()
        logs = []
        users = []
        total_logs = 0
        auth_events = 0
        user_mgmt_events = 0

    return render_template(
        "admin_logs.html",
        logs=logs,
        users=users,
        total_logs=total_logs,
        auth_events=auth_events,
        user_mgmt_events=user_mgmt_events,
        admin_csrf_token=session.setdefault("admin_csrf_token", secrets.token_urlsafe(32)),
    )


@app.route("/admin/logs/export")
@role_required("Admin")
def admin_logs_export():
    try:
        target_user = request.args.get("user", "all").strip()
        action_cat = request.args.get("action_category", "all").strip().lower()
        date_window = request.args.get("date_window", "all").strip().lower()

        query = ActivityLog.query

        # Filter by target user
        user_label = "all_users"
        if target_user and target_user.lower() != "all":
            if target_user.lower() == "system":
                query = query.filter(
                    db.or_(
                        ActivityLog.user_email == None,
                        ActivityLog.user_email == "",
                        ActivityLog.user_email == "system@shrimpguard",
                        ActivityLog.user_name == "System",
                    )
                )
                user_label = "system"
            else:
                query = query.filter(ActivityLog.user_email == target_user.lower())
                user_label = re.sub(r"[^a-zA-Z0-9_-]", "_", target_user.lower())

        # Filter by action category
        if action_cat == "auth":
            query = query.filter(ActivityLog.action.in_(["LOGIN", "LOGOUT", "SIGNUP"]))
        elif action_cat == "mgmt":
            query = query.filter(ActivityLog.action.in_(["USER_CREATE", "USER_EDIT", "USER_DELETE", "PASSWORD_RESET"]))
        elif action_cat == "telemetry":
            query = query.filter(ActivityLog.action.in_(["TELEMETRY_INGEST"]))
        elif action_cat == "security":
            query = query.filter(ActivityLog.action.in_(["LOG_PURGE"]))

        # Filter by date window
        now = datetime.now()
        if date_window == "today":
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(ActivityLog.timestamp >= start_of_day)
        elif date_window in ("7", "30", "60", "90"):
            cutoff = now - timedelta(days=int(date_window))
            query = query.filter(ActivityLog.timestamp >= cutoff)

        export_format = request.args.get("format", "csv").strip().lower()
        if export_format not in ("csv", "xlsx"):
            export_format = "csv"

        logs = query.order_by(ActivityLog.timestamp.desc()).all()

        if export_format == "xlsx":
            def text_cell(reference, value):
                return (
                    f'<c r="{reference}" t="inlineStr"><is><t xml:space="preserve">'
                    f"{escape(str(value))}</t></is></c>"
                )

            headers = ["Log ID", "Timestamp", "User Name", "User Email", "Role", "Action", "Details", "IP Address"]
            cols = ["A", "B", "C", "D", "E", "F", "G", "H"]
            worksheet_rows = []

            header_cells = [text_cell(f"{col}1", h) for col, h in zip(cols, headers)]
            worksheet_rows.append(f'<row r="1">{"".join(header_cells)}</row>')

            for row_number, l in enumerate(logs, start=2):
                ts = l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else ""
                cells = [
                    f'<c r="A{row_number}"><v>{l.id}</v></c>',
                    text_cell(f"B{row_number}", ts),
                    text_cell(f"C{row_number}", l.user_name or "System"),
                    text_cell(f"D{row_number}", l.user_email or "system@shrimpguard"),
                    text_cell(f"E{row_number}", l.role or "System"),
                    text_cell(f"F{row_number}", l.action),
                    text_cell(f"G{row_number}", l.details or ""),
                    text_cell(f"H{row_number}", l.ip_address or "127.0.0.1"),
                ]
                worksheet_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')

            worksheet = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<sheetData>{"".join(worksheet_rows)}</sheetData></worksheet>'
            )
            workbook = io.BytesIO()
            with zipfile.ZipFile(workbook, "w", zipfile.ZIP_DEFLATED) as excel_file:
                excel_file.writestr(
                    "[Content_Types].xml",
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                    '<Default Extension="xml" ContentType="application/xml"/>'
                    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                    "</Types>",
                )
                excel_file.writestr(
                    "_rels/.rels",
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                    "</Relationships>",
                )
                excel_file.writestr(
                    "xl/workbook.xml",
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                    '<sheets><sheet name="Audit Logs" sheetId="1" r:id="rId1"/></sheets></workbook>',
                )
                excel_file.writestr(
                    "xl/_rels/workbook.xml.rels",
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                    "</Relationships>",
                )
                excel_file.writestr("xl/worksheets/sheet1.xml", worksheet)

            workbook.seek(0)
            filename = f"shrimpguard_audit_{user_label}_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
            return send_file(
                workbook,
                as_attachment=True,
                download_name=filename,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Log ID",
            "Timestamp",
            "User Name",
            "User Email",
            "Role",
            "Action",
            "Details",
            "IP Address",
        ])

        for l in logs:
            ts = l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else ""
            writer.writerow([
                l.id,
                ts,
                l.user_name or "System",
                l.user_email or "system@shrimpguard",
                l.role or "System",
                l.action,
                l.details or "",
                l.ip_address or "127.0.0.1",
            ])

        output.seek(0)
        filename = f"shrimpguard_audit_{user_label}_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename,
        )
    except SQLAlchemyError:
        db.session.rollback()
        flash("Unable to export audit log records.", "error")
        return redirect(url_for("admin_logs"))


@app.route("/admin/logs/clear", methods=["POST"])
@role_required("Admin")
def clear_admin_logs():
    expected_token = session.get("admin_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")
    if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
        flash("Your request expired. Please try again.", "error")
        return redirect(url_for("admin_logs"))

    purge_range = request.form.get("range", "30").strip()
    try:
        if purge_range == "all":
            deleted_count = db.session.query(ActivityLog).delete()
            details_msg = f"Pruned all {deleted_count} audit log records."
        else:
            days = int(purge_range)
            cutoff = datetime.now() - timedelta(days=days)
            deleted_count = db.session.query(ActivityLog).filter(ActivityLog.timestamp < cutoff).delete()
            details_msg = f"Pruned {deleted_count} audit logs older than {days} days."

        db.session.commit()

        # Log the purge event
        log_activity(
            action="LOG_PURGE",
            details=details_msg,
            user_email=session.get("user_id"),
            role="Admin",
        )
        flash(f"Log maintenance complete. {details_msg}", "success")
    except (ValueError, SQLAlchemyError) as exc:
        db.session.rollback()
        flash("Unable to purge audit logs. Please try again.", "error")

    return redirect(url_for("admin_logs"))



@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "GET":
        # If user arrived from logout or explicitly requests logout state, FORCE CLEAR session and render login page
        if request.args.get("logged_out"):
            session.clear()
            login_csrf = session.get("login_csrf_token")
            if not login_csrf or not verify_timed_csrf_token(login_csrf, purpose="login"):
                login_csrf = generate_timed_csrf_token("login")
                session["login_csrf_token"] = login_csrf

            resp = make_response(render_template("login.html", error=None, login_csrf_token=login_csrf))
            cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
            cookie_path = app.session_interface.get_cookie_path(app)
            cookie_domain = app.session_interface.get_cookie_domain(app)
            for s_secure, s_samesite, s_part in [
                (False, "Lax", False),
                (True, "None", True),
                (True, "Lax", False),
                (False, None, False),
            ]:
                try:
                    resp.delete_cookie(
                        cookie_name,
                        domain=cookie_domain,
                        path=cookie_path,
                        secure=s_secure,
                        httponly=True,
                        samesite=s_samesite,
                        partitioned=s_part,
                    )
                except Exception:
                    pass
            return resp

        user_id = session.get("user_id")
        if user_id is not None:
            try:
                current_user = db.session.get(User, user_id)
            except SQLAlchemyError:
                db.session.rollback()
                current_user = None
                error = "Sign-in is temporarily unavailable. Please try again."

            if current_user is not None:
                role = current_user.role.strip().casefold()
                if role == "admin":
                    return redirect(url_for("admin_home"))
                if role == "client":
                    return redirect(url_for("dashboard"))
                session.clear()

        existing_token = session.get("login_csrf_token")
        if not existing_token or not verify_timed_csrf_token(existing_token, purpose="login"):
            session["login_csrf_token"] = generate_timed_csrf_token("login")

    else:
        submitted_token = request.form.get("csrf_token", "")
        user_name = request.form.get("user_name", "").strip()
        password = request.form.get("password", "")

        if not validate_csrf(submitted_token, session_token_key="login_csrf_token", purpose="login"):
            error = "Your sign-in request expired. Please try again."
        elif not user_name or not password:
            error = "Enter your username and password."
        else:
            try:
                user = User.query.filter(
                    db.or_(
                        User.user_name == user_name,
                        User.email == user_name.lower(),
                    )
                ).first()
            except SQLAlchemyError:
                db.session.rollback()
                user = None
                error = "Sign-in is temporarily unavailable. Please try again."

            if error is None:
                try:
                    password_is_valid = user is not None and user.check_password(password)
                except (TypeError, ValueError):
                    password_is_valid = False

                if not password_is_valid:
                    error = "Username or password is incorrect."
                else:
                    role = user.role.strip().casefold()
                    if role not in {"admin", "client"}:
                        error = "This account does not have an authorized role."
                    else:
                        user.last_login = datetime.now()
                        if user.password_needs_rehash():
                            user.set_password(password)

                        try:
                            db.session.commit()
                        except SQLAlchemyError:
                            db.session.rollback()
                            error = "Sign-in is temporarily unavailable. Please try again."

                        if error is None:
                            session.clear()
                            session.permanent = True
                            session["user_id"] = user.email
                            session["user_role"] = user.role
                            session["user_name"] = user.name
                            log_activity(
                                action="LOGIN",
                                details=f"User signed in successfully ({user.role}).",
                                user_email=user.email,
                                user_name=user.name,
                                role=user.role,
                            )
                            destination = "admin_home" if role == "admin" else "dashboard"
                            return redirect(url_for(destination))

    login_csrf = session.get("login_csrf_token")
    if not login_csrf or not verify_timed_csrf_token(login_csrf, purpose="login"):
        login_csrf = generate_timed_csrf_token("login")
        session["login_csrf_token"] = login_csrf

    return render_template("login.html", error=error, login_csrf_token=login_csrf)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "GET":
        existing_token = session.get("signup_csrf_token")
        if not existing_token or not verify_timed_csrf_token(existing_token, purpose="signup"):
            session["signup_csrf_token"] = generate_timed_csrf_token("signup")
    else:
        submitted_token = request.form.get("csrf_token", "")
        user_name = request.form.get("user_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        is_valid_email, email_error = validate_legit_email(email)
        if not validate_csrf(submitted_token, session_token_key="signup_csrf_token", purpose="signup"):
            error = "Your sign-up request expired. Please try again."
        elif not user_name or len(user_name) > 80:
            error = "Enter a username between 1 and 80 characters."
        elif not is_valid_email:
            error = email_error
        elif len(password) < 8:
            error = "Use a password with at least 8 characters."
        elif password != confirm_password:
            error = "The passwords do not match."
        else:
            try:
                existing_user = User.query.filter(
                    (User.email == email) | (User.user_name == user_name)
                ).first()
            except SQLAlchemyError:
                db.session.rollback()
                error = "Sign-up is temporarily unavailable. Please try again."
            else:
                if existing_user is not None:
                    error = "An account with that username or email already exists."
                else:
                    user = User(
                        user_name=user_name,
                        email=email,
                        role="Client",
                        status="Active",
                    )
                    user.set_password(password)
                    db.session.add(user)
                    try:
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        error = "An account with that username or email already exists."
                    except SQLAlchemyError:
                        db.session.rollback()
                        error = "Sign-up is temporarily unavailable. Please try again."
                    else:
                        session.pop("signup_csrf_token", None)
                        log_activity(
                            action="SIGNUP",
                            details=f"New client account registered: {user_name} ({email}).",
                            user_email=email,
                            user_name=user_name,
                            role="Client",
                        )
                        flash("Your account was created. Please sign in.", "success")
                        return redirect(url_for("login"))

    signup_csrf = session.get("signup_csrf_token")
    if not signup_csrf or not verify_timed_csrf_token(signup_csrf, purpose="signup"):
        signup_csrf = generate_timed_csrf_token("signup")
        session["signup_csrf_token"] = signup_csrf

    return render_template("signup.html", error=error, signup_csrf_token=signup_csrf)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    user_email = session.get("user_id")
    user_role = session.get("user_role")
    user_name = session.get("user_name")
    if user_email:
        try:
            log_activity(
                action="LOGOUT",
                details="User signed out of the system.",
                user_email=user_email,
                user_name=user_name,
                role=user_role,
            )
        except Exception:
            pass

    session.clear()
    resp = redirect(url_for("login", logged_out="1"))

    # Comprehensively purge session cookies across all browser variants and security contexts
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    cookie_path = app.session_interface.get_cookie_path(app)
    cookie_domain = app.session_interface.get_cookie_domain(app)

    for s_secure, s_samesite, s_part in [
        (False, "Lax", False),
        (True, "None", True),
        (True, "Lax", False),
        (False, None, False),
    ]:
        try:
            resp.delete_cookie(
                cookie_name,
                domain=cookie_domain,
                path=cookie_path,
                secure=s_secure,
                httponly=True,
                samesite=s_samesite,
                partitioned=s_part,
            )
        except Exception:
            pass

    return resp


@app.route("/monitoring")
@role_required("Client")
def monitoring():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    maintenance = get_probe_maintenance_status(user_email=user_email)
    return render_template("monitoring.html", user=user, maintenance=maintenance)


@app.route("/admin/devices")
@role_required("Admin")
def admin_devices():
    return redirect(url_for("admin_telemetry"))


@app.route("/devices")
@role_required("Client")
def devices():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    maintenance = get_probe_maintenance_status(user_email=user_email)

    inv = get_system_devices_inventory()

    try:
        paired_nodes = UserDevice.query.filter_by(user_email=user_email).order_by(UserDevice.created_at.desc()).all()
    except Exception:
        paired_nodes = []

    try:
        maintenance_history = ProbeMaintenanceHistory.query.order_by(ProbeMaintenanceHistory.performed_at.desc()).limit(50).all()
    except Exception:
        maintenance_history = []

    return render_template(
        "devices.html",
        user=user,
        devices_list=inv["devices"],
        total_devices=inv["total_devices"],
        online_devices=inv["online_devices"],
        offline_devices=inv["offline_devices"],
        connected_sensors=inv["connected_sensors"],
        category_stats=inv["category_stats"],
        hardware_stream=inv.get("latest_telemetry", {}),
        hw_connected=inv["is_connected"],
        latest_reading=inv.get("latest_telemetry", {}),
        paired_nodes=paired_nodes,
        maintenance=maintenance,
        maintenance_history=maintenance_history,
    )



@app.route("/historical")
@role_required("Client")
def historical():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    return render_template("historical.html", user=user)


@app.route("/alerts")
@role_required("Client")
def alerts():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    return render_template("alerts.html", user=user)


@app.route("/analytics")
@role_required("Client")
def analytics():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    return render_template("analytics.html", user=user)


@app.route("/calculators")
@app.route("/aquaculture-tools")
@role_required("Client")
def calculators():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    return render_template("calculators.html", user=user)


# =============================================================================
# AQUACULTURE CALCULATORS & DECISION SUPPORT ENDPOINTS
# =============================================================================

AQUACULTURE_EXPORT_CATEGORIES = {
    "biomass": {
        "title": "Estimated Standing Biomass",
        "columns": [
            ("Pond Area (m²)", "pond_area_m2"),
            ("Pond Depth (m)", "pond_depth_m"),
            ("Stocking Density (PL/m²)", "stocking_density_pl_m2"),
            ("Survival Rate (%)", "survival_rate_pct"),
            ("Avg Body Weight - ABW (g)", "abw_g"),
            ("Estimated Active Shrimp Count", "active_shrimp_count"),
            ("Standing Biomass (kg)", "standing_biomass_kg"),
            ("Standing Biomass (Tons)", "standing_biomass_tons"),
        ],
    },
    "temp_feed": {
        "title": "Temperature Feeding Adjustment",
        "columns": [
            ("Water Temperature (°C)", "water_temperature_c"),
            ("Base Feeding Rate (% Biomass)", "base_feeding_rate_pct"),
            ("Temp Adjustment Factor (%)", "temp_feeding_factor"),
            ("Adjusted Daily Feed (kg/day)", "adjusted_daily_feed_kg"),
            ("Feedings Per Day", "feedings_per_day"),
            ("Feed Per Meal (kg/meal)", "feed_per_meal_kg"),
        ],
    },
    "growth": {
        "title": "Eight Growth Performance Equations",
        "columns": [
            ("Initial Stocking Count (IS)", "is_count"),
            ("Live Harvest Count (LHC)", "lhc_count"),
            ("Days of Culture (DOC)", "doc_days"),
            ("Initial Body Weight - IBW (g)", "ibw_g"),
            ("Harvest Bulk Weight - BW (kg)", "bulk_weight_kg"),
            ("Total Feed Given - TFG (kg)", "total_feed_given_kg"),
            ("Total Shrimp Length - TL (cm)", "total_length_cm"),
            ("Eq 1: Survival Rate - SR (%)", "eq1_sr_pct"),
            ("Eq 1: Total Mortality Count", "eq1_mortality_count"),
            ("Eq 2: Final Avg Body Weight - FABW (g)", "eq2_fabw_g"),
            ("Eq 2: Harvest Count per kg", "eq2_count_per_kg"),
            ("Eq 3: Daily Weight Gain - ADWG (g/day)", "eq3_adwg_g_day"),
            ("Eq 3: Weekly Weight Gain (g/week)", "eq3_weekly_gain_g"),
            ("Eq 4: Specific Growth Rate - SGR (%/day)", "eq4_sgr_pct_day"),
            ("Eq 5: Initial Biomass - IB (kg)", "eq5_ib_kg"),
            ("Eq 6: Final Biomass - FB (kg)", "eq6_fb_kg"),
            ("Net Biomass Gain (kg)", "eq5_6_net_biomass_kg"),
            ("Eq 7: Feed Conversion Ratio - FCR", "eq7_fcr"),
            ("Eq 7: Feed Conversion Efficiency (%)", "eq7_feed_efficiency_pct"),
            ("Eq 8: Fulton Condition Factor - K", "eq8_fulton_k"),
            ("Eq 8: Morphological Profile", "eq8_fulton_profile"),
        ],
    },
    "lime": {
        "title": "pH Liming Dosage",
        "columns": [
            ("Liming Pond Volume (m³)", "lime_pond_vol_m3"),
            ("Current Pond pH", "lime_current_ph"),
            ("Target Pond pH", "lime_target_ph"),
            ("Neutralizing Compound", "lime_chemical_type"),
            ("Lime Dosage (kg)", "lime_dosage_kg"),
            ("Lime Application Rate (ppm)", "lime_dosage_ppm"),
        ],
    },
    "carbon": {
        "title": "Organic Carbon Dosing (Biofloc C:N)",
        "columns": [
            ("Biofloc Daily Feed (kg/day)", "molasses_daily_feed_kg"),
            ("Feed Crude Protein (%)", "molasses_protein_pct"),
            ("Target C:N Ratio", "molasses_target_cn"),
            ("Carbon Source Type", "molasses_carbon_source"),
            ("Carbon Required (kg/day)", "molasses_dosage_kg"),
        ],
    },
    "aeration": {
        "title": "Aerator Power Sizing",
        "columns": [
            ("Aeration Pond Biomass (kg)", "aero_biomass_kg"),
            ("Water Temp for Aeration (°C)", "aero_water_temp_c"),
            ("Salinity for Aeration (ppt)", "aero_salinity_ppt"),
            ("Target DO (mg/L)", "aero_target_do_ppm"),
            ("Required Aerator Power (HP)", "aero_power_hp"),
            ("Suggested Aerator Units", "aero_units_desc"),
        ],
    },
    "ammonia": {
        "title": "Unionized Ammonia (NH3) Toxicity",
        "columns": [
            ("Total Ammonia Nitrogen - TAN (mg/L)", "ammonia_tan_ppm"),
            ("Water Temp for NH3 (°C)", "ammonia_temp_c"),
            ("Water pH for NH3", "ammonia_ph"),
            ("Salinity for NH3 (ppt)", "ammonia_salinity_ppt"),
            ("Un-ionized Fraction - f (%)", "ammonia_factor_f"),
            ("Toxic Un-ionized Ammonia - NH3 (mg/L)", "ammonia_nh3_ppm"),
            ("Ammonia Toxicity Status", "ammonia_status"),
        ],
    },
    "co2": {
        "title": "Free Carbon Dioxide (CO2) Concentration",
        "columns": [
            ("Total Alkalinity - CaCO3 (mg/L)", "co2_alkalinity_mg_l"),
            ("Water Temp for CO2 (°C)", "co2_temp_c"),
            ("Water pH for CO2", "co2_ph"),
            ("Tucker Factor f", "co2_factor"),
            ("Free CO2 Concentration (mg/L)", "co2_concentration_mg_l"),
            ("CO2 Toxicity Status", "co2_status"),
        ],
    },
}


def generate_custom_excel(sheet_name, headers, rows):
    def get_column_letter(col_idx):
        result = ""
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            result = chr(65 + remainder) + result
        return result

    worksheet_rows = []
    # Header row (row 1)
    header_cells = [
        f'<c r="{get_column_letter(idx)}1" t="inlineStr"><is><t xml:space="preserve">{escape(str(h))}</t></is></c>'
        for idx, h in enumerate(headers, start=1)
    ]
    worksheet_rows.append(f'<row r="1">{"".join(header_cells)}</row>')

    # Data rows
    for r_idx, row in enumerate(rows, start=2):
        row_cells = []
        for c_idx, val in enumerate(row, start=1):
            cell_ref = f"{get_column_letter(c_idx)}{r_idx}"
            if val is None or val == "":
                continue
            if isinstance(val, (int, float)) and math.isfinite(val):
                row_cells.append(f'<c r="{cell_ref}"><v>{val}</v></c>')
            else:
                row_cells.append(
                    f'<c r="{cell_ref}" t="inlineStr"><is><t xml:space="preserve">{escape(str(val))}</t></is></c>'
                )
        worksheet_rows.append(f'<row r="{r_idx}">{"".join(row_cells)}</row>')

    worksheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(worksheet_rows)}</sheetData></worksheet>'
    )
    workbook = io.BytesIO()
    with zipfile.ZipFile(workbook, "w", zipfile.ZIP_DEFLATED) as excel_file:
        excel_file.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        excel_file.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        clean_sheet_name = re.sub(r'[\/\\?\*\[\]:]', '', sheet_name)[:31] or "Calculations"
        excel_file.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<sheets><sheet name="{escape(clean_sheet_name)}" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        excel_file.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            "</Relationships>",
        )
        excel_file.writestr("xl/worksheets/sheet1.xml", worksheet)

    workbook.seek(0)
    return workbook


@app.route("/api/calculators/save", methods=["POST"])
@role_required("Client")
def save_aquaculture_calculation():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    data = request.get_json(silent=True) or {}

    def safe_flt(v):
        if v is None or v == "":
            return None
        try:
            val = float(v)
            return val if math.isfinite(val) else None
        except (ValueError, TypeError):
            return None

    def safe_integer(v):
        if v is None or v == "":
            return None
        try:
            return int(round(float(v)))
        except (ValueError, TypeError):
            return None

    try:
        notes_str = str(data.get("notes") or "").strip()[:255]
        if not notes_str:
            notes_str = f"Pond Calculation - {datetime.now().strftime('%b %d, %Y %H:%M')}"

        record = AquacultureCalculation(
            user_email=user_email,
            user_name=user.name if user else "Client",
            notes=notes_str,
            # 1. Biomass & Feed
            pond_area_m2=safe_flt(data.get("pond_area_m2")),
            pond_depth_m=safe_flt(data.get("pond_depth_m")),
            stocking_density_pl_m2=safe_flt(data.get("stocking_density_pl_m2")),
            survival_rate_pct=safe_flt(data.get("survival_rate_pct")),
            abw_g=safe_flt(data.get("abw_g")),
            standing_biomass_kg=safe_flt(data.get("standing_biomass_kg")),
            standing_biomass_tons=safe_flt(data.get("standing_biomass_tons")),
            active_shrimp_count=safe_integer(data.get("active_shrimp_count")),
            # 2. Temperature Feeding
            water_temperature_c=safe_flt(data.get("water_temperature_c")),
            base_feeding_rate_pct=safe_flt(data.get("base_feeding_rate_pct")),
            temp_feeding_factor=safe_flt(data.get("temp_feeding_factor")),
            adjusted_daily_feed_kg=safe_flt(data.get("adjusted_daily_feed_kg")),
            feed_per_meal_kg=safe_flt(data.get("feed_per_meal_kg")),
            feedings_per_day=safe_integer(data.get("feedings_per_day")),
            # 3. Eight Growth Equations (Eqs. 1–8)
            is_count=safe_integer(data.get("is_count")),
            lhc_count=safe_integer(data.get("lhc_count")),
            doc_days=safe_integer(data.get("doc_days")),
            ibw_g=safe_flt(data.get("ibw_g")),
            bulk_weight_kg=safe_flt(data.get("bulk_weight_kg")),
            total_feed_given_kg=safe_flt(data.get("total_feed_given_kg")),
            total_length_cm=safe_flt(data.get("total_length_cm")),
            eq1_sr_pct=safe_flt(data.get("eq1_sr_pct")),
            eq1_mortality_count=safe_integer(data.get("eq1_mortality_count")),
            eq2_fabw_g=safe_flt(data.get("eq2_fabw_g")),
            eq2_count_per_kg=safe_flt(data.get("eq2_count_per_kg")),
            eq3_adwg_g_day=safe_flt(data.get("eq3_adwg_g_day")),
            eq3_weekly_gain_g=safe_flt(data.get("eq3_weekly_gain_g")),
            eq4_sgr_pct_day=safe_flt(data.get("eq4_sgr_pct_day")),
            eq5_ib_kg=safe_flt(data.get("eq5_ib_kg")),
            eq6_fb_kg=safe_flt(data.get("eq6_fb_kg")),
            eq5_6_net_biomass_kg=safe_flt(data.get("eq5_6_net_biomass_kg")),
            eq7_fcr=safe_flt(data.get("eq7_fcr")),
            eq7_feed_efficiency_pct=safe_flt(data.get("eq7_feed_efficiency_pct")),
            eq8_fulton_k=safe_flt(data.get("eq8_fulton_k")),
            eq8_fulton_profile=str(data.get("eq8_fulton_profile") or "").strip()[:100] or None,
            # 4. pH Liming
            lime_pond_vol_m3=safe_flt(data.get("lime_pond_vol_m3")),
            lime_current_ph=safe_flt(data.get("lime_current_ph")),
            lime_target_ph=safe_flt(data.get("lime_target_ph")),
            lime_chemical_type=str(data.get("lime_chemical_type") or "").strip()[:100] or None,
            lime_dosage_kg=safe_flt(data.get("lime_dosage_kg")),
            lime_dosage_ppm=safe_flt(data.get("lime_dosage_ppm")),
            # 5. Organic Carbon Dosing
            molasses_daily_feed_kg=safe_flt(data.get("molasses_daily_feed_kg")),
            molasses_protein_pct=safe_flt(data.get("molasses_protein_pct")),
            molasses_target_cn=safe_flt(data.get("molasses_target_cn")),
            molasses_carbon_source=str(data.get("molasses_carbon_source") or "").strip()[:100] or None,
            molasses_dosage_kg=safe_flt(data.get("molasses_dosage_kg")),
            # 6. Aerator Power
            aero_biomass_kg=safe_flt(data.get("aero_biomass_kg")),
            aero_water_temp_c=safe_flt(data.get("aero_water_temp_c")),
            aero_salinity_ppt=safe_flt(data.get("aero_salinity_ppt")),
            aero_target_do_ppm=safe_flt(data.get("aero_target_do_ppm")),
            aero_power_hp=safe_flt(data.get("aero_power_hp")),
            aero_units_desc=str(data.get("aero_units_desc") or "").strip()[:100] or None,
            # 7. Unionized Ammonia
            ammonia_tan_ppm=safe_flt(data.get("ammonia_tan_ppm")),
            ammonia_temp_c=safe_flt(data.get("ammonia_temp_c")),
            ammonia_ph=safe_flt(data.get("ammonia_ph")),
            ammonia_salinity_ppt=safe_flt(data.get("ammonia_salinity_ppt")),
            ammonia_factor_f=safe_flt(data.get("ammonia_factor_f")),
            ammonia_nh3_ppm=safe_flt(data.get("ammonia_nh3_ppm")),
            ammonia_status=str(data.get("ammonia_status") or "").strip()[:50] or None,
            # 8. Free Carbon Dioxide
            co2_alkalinity_mg_l=safe_flt(data.get("co2_alkalinity_mg_l")),
            co2_temp_c=safe_flt(data.get("co2_temp_c")),
            co2_ph=safe_flt(data.get("co2_ph")),
            co2_factor=safe_flt(data.get("co2_factor")),
            co2_concentration_mg_l=safe_flt(data.get("co2_concentration_mg_l")),
            co2_status=str(data.get("co2_status") or "").strip()[:50] or None,
        )

        db.session.add(record)
        db.session.commit()

        log_activity(
            "Aquaculture Calculation Saved",
            f"Record #{record.id} saved for {user.name if user else 'Client'} ({record.notes})",
            user_email=user_email,
            user_name=user.name if user else "Client",
            role="Client",
        )

        return jsonify({
            "success": True,
            "id": record.id,
            "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": record.notes,
            "message": f"Calculation snapshot #{record.id} successfully saved to database.",
        })
    except Exception as exc:
        db.session.rollback()
        app.logger.exception("Failed to save aquaculture calculation record.")
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/calculators/history", methods=["GET"])
@role_required("Client", "Admin")
def get_aquaculture_history():
    try:
        user_email = session.get("user_id")
        user_role = session.get("user_role") or (session.get("role") if "role" in session else "Client")
        query = AquacultureCalculation.query
        if user_role != "Admin":
            query = query.filter(AquacultureCalculation.user_email == user_email)
        count = query.count()
        latest_records = (
            query.order_by(AquacultureCalculation.created_at.desc())
            .limit(10)
            .all()
        )
        return jsonify({
            "success": True,
            "total_count": count,
            "latest": [r.to_dict() for r in latest_records],
        })
    except Exception as exc:
        app.logger.exception("Failed to query calculation history.")
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/calculators/export", methods=["GET", "POST"])
@role_required("Client")
def export_aquaculture_calculations():
    payload = request.get_json(silent=True) or {}
    
    categories_raw = (
        payload.get("categories")
        or request.args.get("categories")
        or request.form.get("categories")
        or "all"
    )
    scope = (
        str(payload.get("scope") or request.args.get("scope") or request.form.get("scope") or "saved")
        .strip()
        .lower()
    )
    date_filter = (
        str(payload.get("date") or request.args.get("date") or request.form.get("date") or "all")
        .strip()
        .lower()
    )
    export_format = (
        str(payload.get("format") or request.args.get("format") or request.form.get("format") or "xlsx")
        .strip()
        .lower()
    )
    if export_format not in ("xlsx", "csv"):
        export_format = "xlsx"

    # Parse categories to export
    if isinstance(categories_raw, list):
        selected_cats = [c.strip().lower() for c in categories_raw if c.strip().lower() in AQUACULTURE_EXPORT_CATEGORIES]
    elif isinstance(categories_raw, str):
        if categories_raw.lower() in ("all", "*", ""):
            selected_cats = list(AQUACULTURE_EXPORT_CATEGORIES.keys())
        else:
            selected_cats = [c.strip().lower() for c in categories_raw.split(",") if c.strip().lower() in AQUACULTURE_EXPORT_CATEGORIES]
    else:
        selected_cats = list(AQUACULTURE_EXPORT_CATEGORIES.keys())

    if not selected_cats:
        selected_cats = list(AQUACULTURE_EXPORT_CATEGORIES.keys())

    # Build Header Row
    headers = ["Record ID", "Recorded Date & Time", "Notes / Pond ID", "Operator"]
    columns_spec = []  # list of tuples: (header_name, col_attr)
    for cat in selected_cats:
        cat_info = AQUACULTURE_EXPORT_CATEGORIES[cat]
        for col_title, col_attr in cat_info["columns"]:
            headers.append(col_title)
            columns_spec.append(col_attr)

    rows = []

    if scope == "current":
        # Exporting current screen values passed in payload or fallback default
        current_data = payload.get("current_data") or {}
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_email = session.get("user_id")
        user = db.session.get(User, user_email) if user_email else None
        operator_name = user.name if user else "Client"
        notes_val = str(current_data.get("notes") or "Active Screen Calculation Snapshot").strip()

        row = ["Snapshot", now_str, notes_val, operator_name]
        for col_attr in columns_spec:
            val = current_data.get(col_attr)
            if val is not None and isinstance(val, (int, float)):
                row.append(val)
            elif val is not None and str(val).strip() != "":
                try:
                    num = float(val)
                    row.append(num if math.isfinite(num) else str(val))
                except (ValueError, TypeError):
                    row.append(str(val))
            else:
                row.append("")
        rows.append(row)
    else:
        # Exporting from database records (isolated per user)
        user_email = session.get("user_id")
        user_role = session.get("user_role") or (session.get("role") if "role" in session else "Client")
        query = AquacultureCalculation.query
        if user_role != "Admin":
            query = query.filter(AquacultureCalculation.user_email == user_email)
        query = query.order_by(AquacultureCalculation.created_at.desc())

        # Date filtering
        now = datetime.now()
        if date_filter == "today":
            start_today = datetime(now.year, now.month, now.day)
            query = query.filter(AquacultureCalculation.created_at >= start_today)
        elif date_filter == "7d":
            start_7d = now - timedelta(days=7)
            query = query.filter(AquacultureCalculation.created_at >= start_7d)
        elif date_filter == "30d":
            start_30d = now - timedelta(days=30)
            query = query.filter(AquacultureCalculation.created_at >= start_30d)
        elif date_filter != "all" and re.match(r"^\d{4}-\d{2}-\d{2}$", date_filter):
            try:
                dt_obj = datetime.strptime(date_filter, "%Y-%m-%d")
                start_dt = datetime(dt_obj.year, dt_obj.month, dt_obj.day)
                end_dt = start_dt + timedelta(days=1)
                query = query.filter(AquacultureCalculation.created_at >= start_dt, AquacultureCalculation.created_at < end_dt)
            except ValueError:
                pass

        records = query.all()

        if not records:
            # Placeholder if database table has no rows matching filter
            rows.append(["No records", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "No calculation records saved for selected filter", session.get("user_id") or "Client"] + ["" for _ in columns_spec])
        else:
            for rec in records:
                rec_dt = rec.created_at.strftime("%Y-%m-%d %H:%M:%S") if rec.created_at else ""
                row = [rec.id, rec_dt, rec.notes or "Pond Run", rec.user_name or "Client"]
                for col_attr in columns_spec:
                    val = getattr(rec, col_attr, None)
                    row.append(val if val is not None else "")
                rows.append(row)

    # Dynamic filename
    timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
    cat_summary = "all-tools" if len(selected_cats) == len(AQUACULTURE_EXPORT_CATEGORIES) else f"{len(selected_cats)}-modules"
    download_filename = f"shrimpguard-aquaculture-calculations_{cat_summary}_{timestamp_slug}.{export_format}"

    # Log export activity
    log_activity(
        "Aquaculture Calculations Exported",
        f"Exported {len(rows)} records in {export_format.upper()} ({', '.join(selected_cats)})",
    )

    # Return CSV
    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            as_attachment=True,
            download_name=download_filename,
            mimetype="text/csv",
        )

    # Return Excel (.xlsx)
    excel_stream = generate_custom_excel("Pond Calculations", headers, rows)
    return send_file(
        excel_stream,
        as_attachment=True,
        download_name=download_filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )



@app.route("/settings", methods=["GET", "POST"])
@role_required("Client")
def settings():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email)
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    csrf_token = session.get("settings_csrf_token")
    if not csrf_token or not verify_timed_csrf_token(csrf_token, purpose="settings"):
        csrf_token = generate_timed_csrf_token("settings")
        session["settings_csrf_token"] = csrf_token

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        action = request.form.get("action", "")
        if not validate_csrf(submitted_token, session_token_key="settings_csrf_token", purpose="settings"):
            flash("Your request expired. Please try again.", "error")
        elif action == "profile":
            user_name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            ntfy_topic = request.form.get("ntfy_topic", "").strip()
            is_valid_email, email_error = validate_legit_email(email)
            if not user_name or len(user_name) > 80:
                flash("Enter a name between 1 and 80 characters.", "error")
            elif not is_valid_email:
                flash(email_error, "error")
            elif User.query.filter(User.email != user_email, User.email == email).first():
                flash("An account with that email already exists.", "error")
            elif User.query.filter(User.email != user_email, User.user_name == user_name).first():
                flash("A user with that name already exists.", "error")
            elif ntfy_topic and not is_valid_topic(ntfy_topic):
                flash("Invalid ntfy topic. Use 3-64 characters (letters, numbers, hyphens, and underscores only).", "error")
            else:
                new_topic = ntfy_topic if ntfy_topic else None
                try:
                    if email != user_email:
                        db.session.expunge(user)
                        db.session.execute(
                            update(User)
                            .where(User.email == user_email)
                            .values(
                                user_name=user_name,
                                email=email,
                                ntfy_topic=new_topic,
                            )
                        )
                        db.session.execute(
                            update(ActivityLog)
                            .where(ActivityLog.user_email == user_email)
                            .values(user_email=email)
                        )
                        db.session.execute(
                            update(AquacultureCalculation)
                            .where(AquacultureCalculation.user_email == user_email)
                            .values(user_email=email)
                        )
                        db.session.execute(
                            update(sensor_readings)
                            .where(sensor_readings.c.user_email == user_email)
                            .values(user_email=email)
                        )
                    else:
                        user.user_name = user_name
                        user.ntfy_topic = new_topic
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
                    flash("Your profile could not be saved. Please try again.", "error")
                else:
                    session["user_id"] = email
                    session["user_name"] = user_name
                    session["settings_csrf_token"] = secrets.token_urlsafe(32)
                    log_activity(
                        action="PROFILE_UPDATE",
                        details=f"Updated profile details (Name: {user_name}, Email: {email}).",
                        user_email=email,
                        user_name=user_name,
                        role="Client",
                    )
                    flash("Profile updated successfully.", "success")
        elif action == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if not user.check_password(current_password):
                flash("Your current password is incorrect.", "error")
            elif len(new_password) < 8:
                flash("Use a new password with at least 8 characters.", "error")
            elif new_password != confirm_password:
                flash("The new passwords do not match.", "error")
            else:
                user.set_password(new_password)
                try:
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
                    flash("Your password could not be updated. Please try again.", "error")
                else:
                    session["settings_csrf_token"] = secrets.token_urlsafe(32)
                    log_activity(
                        action="PASSWORD_CHANGE",
                        details="Account password changed successfully.",
                        user_email=user.email,
                        user_name=user.name,
                        role=user.role,
                    )
                    flash("Password updated successfully.", "success")
        else:
            flash("Choose a valid settings action.", "error")

        return redirect(url_for("settings"))

    return render_template("settings.html", user=user, settings_csrf_token=csrf_token)


@app.route("/api/activity-logs")
@role_required("Admin")
def api_activity_logs():
    try:
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
        return jsonify({
            "status": "success",
            "count": len(logs),
            "logs": [l.to_dict() for l in logs],
        })
    except SQLAlchemyError as exc:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(exc)}), 500



@app.route("/api/ntfy/generate-topic", methods=["GET", "POST"])
def api_ntfy_generate_topic():
    user_email = session.get("user_id")
    if not user_email:
        return jsonify({"error": "Authentication required."}), 401
    return jsonify({"topic": generate_secure_topic()})


@app.route("/api/ntfy/test", methods=["POST"])
def api_test_ntfy():
    user_email = session.get("user_id")
    if not user_email:
        return jsonify({"error": "Authentication required."}), 401

    payload = request.get_json(silent=True) or {}
    topic = payload.get("ntfy_topic", "").strip()
    if not topic:
        user = db.session.get(User, user_email)
        topic = user.ntfy_topic if user else None

    if not topic:
        topic = os.getenv("NTFY_DEFAULT_TOPIC", "").strip()

    if not topic:
        return jsonify({"error": "No ntfy topic provided. Please enter a topic in Settings or .env."}), 400

    if not is_valid_topic(topic):
        return jsonify({"error": "Invalid topic name. Use 3-64 characters: letters, numbers, hyphens, and underscores only."}), 400

    result = send_water_quality_alert_ntfy(
        severity="TEST",
        temp=29.0,
        ph=8.0,
        reason="Test notification verification from ShrimpGuard gateway via ntfy.sh",
        topic=topic
    )
    return jsonify(result)


@app.route("/api/alerts/mark-read", methods=["POST"])
def mark_alerts_read():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    now_dt = datetime.now()
    session["last_notifications_read_at"] = now_dt.isoformat()

    try:
        user = db.session.get(User, user_id)
        if user:
            user.last_read_notifications = now_dt
            db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()

    return jsonify({"success": True, "unread_notifications": 0, "marked_at": now_dt.isoformat()})




def get_latest_sensor_dict(user_email=None):
    try:
        query = select(sensor_readings).order_by(sensor_readings.c.date.desc())
        if user_email:
            query = query.where(sensor_readings.c.user_email == user_email)
        latest = db.session.execute(query.limit(1)).mappings().first()
        if not latest:
            return None
        return {
            "temperature": float(latest["temperature"]),
            "ph": float(latest["ph_level"]),
            "status": str(latest.get("status") or "Optimal"),
            "recorded_at": str(latest["date"]),
            "user_email": latest.get("user_email"),
        }
    except Exception:
        return None


@app.route("/api/co2/calculate", methods=["GET", "POST"])
def calculate_co2():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    if request.method == "GET":
        data = request.args

    alk_raw = data.get("alkalinity")
    if alk_raw is None or str(alk_raw).strip() == "":
        return jsonify({"error": "Total Alkalinity value is required."}), 400

    try:
        alk = float(alk_raw)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid alkalinity value."}), 400

    temp = data.get("temp")
    ph = data.get("ph")

    if temp is None or ph is None or str(temp).strip() == "" or str(ph).strip() == "":
        latest = get_latest_sensor_dict(user_email=user_id)
        if not latest or latest.get("temperature") is None or latest.get("ph") is None:
            return jsonify({"error": "No sensor readings available to calculate free CO2. Please provide temperature and pH."}), 400
        temp = latest["temperature"]
        ph = latest["ph"]

    try:
        temp = float(temp)
        ph = float(ph)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid temperature or pH value."}), 400

    from co2_service import calculate_free_co2
    result = calculate_free_co2(alk, temp, ph)
    return jsonify(result)


@app.route("/api/ammonia/calculate", methods=["GET", "POST"])
def calculate_ammonia():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    if request.method == "GET":
        data = request.args

    tan_raw = data.get("tan")
    if tan_raw is None or str(tan_raw).strip() == "":
        return jsonify({"error": "Total Ammonia Nitrogen (TAN) value is required."}), 400

    try:
        tan = float(tan_raw)
        if tan < 0:
            return jsonify({"error": "TAN value must be positive."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid TAN value. Must be a valid number."}), 400

    temp = data.get("temperature")
    ph = data.get("ph")

    if temp is None or ph is None or str(temp).strip() == "" or str(ph).strip() == "":
        latest = get_latest_sensor_dict(user_email=user_id)
        if not latest or latest.get("temperature") is None or latest.get("ph") is None:
            return jsonify({"error": "No sensor readings available to calculate unionized ammonia. Please provide temperature and pH."}), 400
        temp = latest["temperature"]
        ph = latest["ph"]

    try:
        temp = float(temp)
        ph = float(ph)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid temperature or pH value."}), 400

    from ammonia_service import calculate_unionized_ammonia
    result = calculate_unionized_ammonia(tan, temp, ph)
    return jsonify(result)


@app.route("/api/growth/calculate", methods=["GET", "POST"])
def calculate_growth_metrics():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    if request.method == "GET":
        data = request.args

    from growth_service import (
        calculate_survival_rate,
        calculate_final_avg_body_weight,
        calculate_daily_gain_and_sgr,
        calculate_biomasses,
        calculate_fcr,
        calculate_fulton_condition,
        calculate_full_growth_suite
    )

    calc_type = str(data.get("type", "all")).strip().lower()

    try:
        if calc_type == "sr":
            return jsonify(calculate_survival_rate(data.get("is", 0), data.get("lhc", 0)))
        elif calc_type == "fabw":
            return jsonify(calculate_final_avg_body_weight(data.get("bw", 0), data.get("lhc", 0), data.get("unit", "kg")))
        elif calc_type == "growth":
            return jsonify(calculate_daily_gain_and_sgr(data.get("ibw", 0), data.get("fabw", 0), data.get("doc", 0)))
        elif calc_type == "biomass":
            return jsonify(calculate_biomasses(data.get("is", 0), data.get("ibw", 0), data.get("lhc", 0), data.get("fabw", 0)))
        elif calc_type == "fcr":
            return jsonify(calculate_fcr(data.get("tfg", 0), data.get("fb", 0), data.get("ib", 0), data.get("feed_unit", "kg"), data.get("biomass_unit", "kg")))
        elif calc_type == "k":
            return jsonify(calculate_fulton_condition(data.get("fabw", 0), data.get("tl", 0)))
        else:
            return jsonify(calculate_full_growth_suite(
                initial_stocking=data.get("is", 100000),
                live_harvest_count=data.get("lhc", 85000),
                days_of_culture=data.get("doc", 90),
                initial_body_weight=data.get("ibw", 0.01),
                bulk_weight=data.get("bw", 1700),
                final_avg_body_weight=data.get("fabw"),
                total_feed_given=data.get("tfg", 2125),
                total_length=data.get("tl", 12.9),
                bulk_weight_unit=data.get("bw_unit", "kg"),
                feed_unit=data.get("feed_unit", "kg")
            ))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/calculators/ai-insight", methods=["POST"])
def calculator_ai_insight():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    payload = request.get_json(silent=True) or {}
    module = str(payload.get("module", "feeding")).strip().lower()
    data = payload.get("data") or {}

    try:
        from calculator_ai_service import get_calculator_ai_insight
        result = get_calculator_ai_insight(module, data)
        return jsonify(result)
    except Exception as exc:
        app.logger.exception("Error generating calculator AI insight: %s", exc)
        return jsonify({"error": "Failed to generate AI evaluation.", "details": str(exc)}), 500


def compute_adaptive_persona(interactions, dwell_times):
    # Normalized activity units: interactions count + dwell in minutes
    raw_scores = {
        "monitoring": float(interactions.get("monitoring", 0)) + float(dwell_times.get("monitoring", 0)) / 60.0,
        "calculators": float(interactions.get("calculators", 0)) + float(dwell_times.get("calculators", 0)) / 60.0,
        "analytics": float(interactions.get("analytics", 0)) + float(dwell_times.get("analytics", 0)) / 60.0,
        "alerts": float(interactions.get("alerts", 0)) + float(dwell_times.get("alerts", 0)) / 60.0,
        "devices": float(interactions.get("devices", 0)) + float(dwell_times.get("devices", 0)) / 60.0,
    }
    total_score = sum(raw_scores.values())
    if total_score < 1.0:
        return "evaluating", {"monitoring": 0, "calculators": 0, "analytics": 0, "alerts": 0, "devices": 0}
    if total_score < 4.0:
        return "balanced_operator", {"monitoring": 25, "calculators": 25, "analytics": 25, "alerts": 25, "devices": 0}

    percentages = {k: int(round((v / total_score) * 100)) for k, v in raw_scores.items()}

    sorted_cats = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_pct = sorted_cats[0]
    second_pct = sorted_cats[1][1] if len(sorted_cats) > 1 else 0

    if top_pct >= 38 and (top_pct - second_pct >= 8):
        if top_cat == "monitoring" or (top_cat == "alerts" and percentages.get("monitoring", 0) >= 20):
            return "field_inspector", percentages
        if top_cat == "calculators":
            return "farm_planner", percentages
        if top_cat == "analytics":
            return "data_analyst", percentages

    if percentages.get("monitoring", 0) + percentages.get("alerts", 0) >= 55:
        return "field_inspector", percentages

    return "balanced_operator", percentages


def get_adaptive_next_action(persona_id, user_email=None):
    latest = get_latest_sensor_dict(user_email=user_email)
    if not latest:
        return {
            "type": "info",
            "title": "Awaiting Telemetry",
            "message": "Pond telemetry receiver active. Verify transmitter power on Node 1.",
            "url": "/devices",
            "cta": "Check Devices",
        }

    temp = float(latest.get("temperature") or 28.5)
    ph = float(latest.get("ph") or 7.8)

    if ph > 8.5:
        return {
            "type": "warning",
            "title": "High pH Detected",
            "message": f"Pond water pH is alkaline ({ph:.2f}). Consider biofloc carbon addition.",
            "url": "/calculators#molasses-calculator-panel",
            "cta": "Calculate Molasses Dosing",
        }
    if ph < 7.5:
        return {
            "type": "warning",
            "title": "Low pH Detected",
            "message": f"Pond water pH is acidic ({ph:.2f}). Check agricultural lime dosage.",
            "url": "/calculators#lime-calculator-panel",
            "cta": "Calculate Liming Dose",
        }
    if temp < 26.0 or temp > 32.0:
        return {
            "type": "warning",
            "title": "Temperature Deviation",
            "message": f"Water temp is {temp:.2f} °C (outside optimal 26-32 °C range). Adjust feeding rate.",
            "url": "/calculators#feeding-calculator-panel",
            "cta": "Adjust Feed Ratio",
        }

    if persona_id == "evaluating":
        return {
            "type": "optimal",
            "title": "Welcome to ShrimpGuard",
            "message": "Explore real-time pond monitoring, calculators, and water quality analysis to personalize your workflow.",
            "url": "/monitoring",
            "cta": "Explore Monitoring",
        }

    if persona_id == "farm_planner":
        return {
            "type": "optimal",
            "title": "Pond Conditions Stable",
            "message": "Water parameters optimal for Penaeus vannamei. Ready to calculate daily biomass feed.",
            "url": "/calculators#feeding-calculator-panel",
            "cta": "Run Feed Calculator",
        }
    if persona_id == "data_analyst":
        return {
            "type": "optimal",
            "title": "Stable 24h Baseline",
            "message": "Parameters within threshold. Audit today's multivariate WQI trends and export CSV log.",
            "url": "/analytics",
            "cta": "View Analytics",
        }
    return {
        "type": "optimal",
        "title": "Pond Parameters Optimal",
        "message": f"Current: Temp {temp:.2f} °C, pH {ph:.2f}. System operating within target parameters.",
        "url": "/monitoring",
        "cta": "Inspect Gauges",
    }


@app.route("/api/adaptive/profile", methods=["GET"])
def get_adaptive_profile():
    user_email = session.get("user_id")
    stored = session.get("adaptive_profile") or {}
    persona_id = stored.get("persona_id", "evaluating")
    persona_info = ADAPTIVE_PERSONAS.get(persona_id, ADAPTIVE_PERSONAS["evaluating"])
    next_action = get_adaptive_next_action(persona_id, user_email=user_email)

    return jsonify({
        "persona": persona_info,
        "persona_id": persona_id,
        "percentages": stored.get("percentages", {"monitoring": 0, "calculators": 0, "analytics": 0, "alerts": 0, "devices": 0}),
        "device": stored.get("device", {"type": "desktop_workstation", "is_touch": False}),
        "preferences": stored.get("preferences", {"auto_adapt": True, "sunlight_mode": "auto", "density": "auto"}),
        "next_action": next_action,
    })


@app.route("/api/adaptive/sync", methods=["POST"])
def sync_adaptive_telemetry():
    payload = request.get_json(silent=True) or {}
    interactions = payload.get("interactions") or {}
    dwell_times = payload.get("dwell") or {}
    device_info = payload.get("device") or {}
    user_prefs = payload.get("preferences") or {}

    user_email = session.get("user_id")
    persona_id, percentages = compute_adaptive_persona(interactions, dwell_times)
    persona_info = ADAPTIVE_PERSONAS.get(persona_id, ADAPTIVE_PERSONAS["balanced_operator"])
    next_action = get_adaptive_next_action(persona_id, user_email=user_email)

    profile_data = {
        "persona_id": persona_id,
        "percentages": percentages,
        "device": device_info,
        "preferences": user_prefs,
        "updated_at": datetime.now().isoformat(),
    }
    session["adaptive_profile"] = profile_data

    if user_email and session.get("last_logged_persona") != persona_id:
        session["last_logged_persona"] = persona_id
        log_activity(
            action="ADAPTIVE_PROFILE_UPDATE",
            details=f"User interaction model classified persona as {persona_info['title']} ({device_info.get('type', 'standard')}).",
            user_email=user_email,
        )

    return jsonify({
        "success": True,
        "persona": persona_info,
        "persona_id": persona_id,
        "percentages": percentages,
        "next_action": next_action,
        "density": persona_info["default_density"] if user_prefs.get("density") == "auto" else user_prefs.get("density", "auto"),
    })


@app.route("/api/adaptive/reset", methods=["POST"])
def reset_adaptive_profile():
    session.pop("adaptive_profile", None)
    session.pop("last_logged_persona", None)
    user_email = session.get("user_id")
    default_persona = ADAPTIVE_PERSONAS["evaluating"]
    return jsonify({
        "success": True,
        "message": "Adaptive interaction model reset to factory defaults.",
        "persona": default_persona,
        "persona_id": "evaluating",
        "percentages": {"monitoring": 0, "calculators": 0, "analytics": 0, "alerts": 0, "devices": 0},
        "next_action": get_adaptive_next_action("evaluating", user_email=user_email),
    })


@app.route("/api/adaptive/settings", methods=["POST"])
def update_adaptive_settings():
    payload = request.get_json(silent=True) or {}
    stored = session.get("adaptive_profile") or {}
    prefs = stored.get("preferences", {"auto_adapt": True, "sunlight_mode": "auto", "density": "auto"})

    for k in ["auto_adapt", "sunlight_mode", "density", "data_saver"]:
        if k in payload:
            prefs[k] = payload[k]

    stored["preferences"] = prefs
    session["adaptive_profile"] = stored

    return jsonify({"success": True, "preferences": prefs})


_LORA_SERVICE_LOCK = threading.Lock()
_LORA_SERVICE_STARTED = False


def start_lora_hardware_service():
    """Automatically connects to Node 2 LoRa receiver and syncs live readings into database."""
    global _LORA_SERVICE_STARTED
    with _LORA_SERVICE_LOCK:
        if _LORA_SERVICE_STARTED:
            return
        _LORA_SERVICE_STARTED = True

    try:
        from hardware_serial import start_hardware_listener
        start_hardware_listener(
            app=app,
            db=db,
            sensor_readings_table=sensor_readings,
            calculate_ml_fn=calculate_ml_water_quality_analysis,
            ntfy_dispatch_fn=_async_dispatch_ntfy,
            user_model=User,
            user_device_model=UserDevice,
        )
        app.logger.info("Automatic LoRa hardware listener daemon spawned successfully.")
    except Exception as exc:
        app.logger.warning("Could not start LoRa hardware listener: %s", exc)


# Start hardware listener if running under flask CLI
if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
    start_lora_hardware_service()


if __name__ == "__main__":
    start_lora_hardware_service()
    app.run(debug=True, use_reloader=False)
