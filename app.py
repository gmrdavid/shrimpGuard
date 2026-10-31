import csv
import hmac
import io
import math
import os
import re
import secrets
import threading
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from xml.sax.saxutils import escape

from flask import Flask, flash, has_request_context, jsonify, redirect, render_template, request, send_file, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, insert, select, text
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


app.config["SECRET_KEY"] = load_secret_key()
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True


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
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# --- TABLE 1: SENSORS ---
sensor_readings = db.Table(
    "sensors",
    db.metadata,
    db.Column("ph_level", db.Float, nullable=False),
    db.Column("temperature", db.Float, nullable=False),
    db.Column("date", db.String(45), primary_key=True, nullable=False),
    db.Column("status", db.String(45), nullable=False),
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


@app.context_processor
def inject_logout_csrf_token():
    user_email = session.get("user_id")
    if user_email is None:
        return {"logout_csrf_token": "", "current_user": None}
    current_u = None
    try:
        current_u = db.session.get(User, user_email)
    except Exception:
        pass
    return {
        "logout_csrf_token": session.setdefault(
            "logout_csrf_token", secrets.token_urlsafe(32)
        ),
        "current_user": current_u,
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


def role_required(required_role):
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
            if actual_role != required_role.casefold():
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
@role_required("Client")
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
                users_with_topic = db.session.query(User).filter(User.ntfy_topic.isnot(None), User.ntfy_topic != "").all()
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
@role_required("Client")
def latest_reading():
    try:
        readings = db.session.execute(
            select(sensor_readings)
        ).mappings().all()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load the latest sensor reading.")
        return jsonify({"error": "Unable to load sensor readings."}), 503
    if not readings:
        return jsonify(None)
    latest = max(readings, key=parse_reading_datetime)
    return jsonify(serialize_sensor_reading(latest))


@app.route("/api/wqi/calculate", methods=["GET", "POST"])
@role_required("Client")
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
@role_required("Client")
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
@role_required("Client")
def reading_history():
    try:
        readings = db.session.execute(
            select(sensor_readings)
        ).mappings().all()
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
        status_label = "Active" if is_active else "Resolved"

        if is_abnormal:
            severity = ml_status
            if temp_abnormal and ph_abnormal:
                alert_type = "combined"
                title = f"{severity} Combined Water Quality Alert"
                message = f"ML model detected {severity} condition: Water temperature is {temp:.1f} °C (optimal: 28.0–32.0 °C) and pH is {ph:.2f} (optimal: 7.50–8.50)."
                notification = f"Push: [{severity.upper()}] Temp {temp:.1f}°C, pH {ph:.2f}. Immediate pond management required."
            elif temp_abnormal:
                alert_type = "temperature"
                title = f"{severity} Temperature Alert"
                message = f"ML model detected {severity} temperature: Currently {temp:.1f} °C, outside optimal range of 28.0–32.0 °C."
                notification = f"Push: [{severity.upper()}] Pond water temperature is {temp:.1f}°C. Check aeration/temperature controls."
            elif ph_abnormal:
                alert_type = "ph"
                title = f"{severity} pH Level Alert"
                message = f"ML model detected {severity} pH level: Currently {ph:.2f}, outside optimal range of 7.50–8.50."
                notification = f"Push: [{severity.upper()}] Pond water pH is {ph:.2f}. Adjust water treatment and buffering."
            else:
                alert_type = "general"
                title = f"{severity} Water Quality Alert"
                message = f"ML model classified pond condition as {severity} (Temp: {temp:.1f} °C, pH: {ph:.2f})."
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

    try:
        readings = db.session.execute(
            select(sensor_readings)
            .order_by(sensor_readings.c.date.desc())
        ).mappings().all()
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
    resolved_count = len(readings) - len(active_alerts)
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
        status_label = "Active" if (idx == 0 and is_abnormal) else "Resolved"

        r_dt = parse_reading_datetime({"date": date_str})
        is_read = bool(last_read and r_dt <= last_read)

        if is_abnormal:
            severity = ml_status
            if temp_abnormal and ph_abnormal:
                alert_type = "combined"
                title = f"{severity} Combined Water Quality Alert"
                message = f"ML model detected {severity} condition: Water temperature is {temp:.1f} °C (optimal: 28.0–32.0 °C) and pH is {ph:.2f} (optimal: 7.50–8.50)."
                notification = f"Push: [{severity.upper()}] Temp {temp:.1f}°C, pH {ph:.2f}. Immediate pond management required."
            elif temp_abnormal:
                alert_type = "temperature"
                title = f"{severity} Temperature Alert"
                message = f"ML model detected {severity} temperature: Currently {temp:.1f} °C, outside optimal range of 28.0–32.0 °C."
                notification = f"Push: [{severity.upper()}] Pond water temperature is {temp:.1f}°C. Check aeration/temperature controls."
            elif ph_abnormal:
                alert_type = "ph"
                title = f"{severity} pH Level Alert"
                message = f"ML model detected {severity} pH level: Currently {ph:.2f}, outside optimal range of 7.50–8.50."
                notification = f"Push: [{severity.upper()}] Pond water pH is {ph:.2f}. Adjust water treatment and buffering."
            else:
                alert_type = "general"
                title = f"{severity} Water Quality Alert"
                message = f"ML model classified pond condition as {severity} (Temp: {temp:.1f} °C, pH: {ph:.2f})."
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
                "message": f"Normal telemetry logged: Water temperature is {temp:.1f} °C and pH is {ph:.2f}, meeting optimal Penaeus vannamei standards.",
                "notification": f"Telemetry: [OPTIMAL] Temp {temp:.1f}°C, pH {ph:.2f}. All parameters within normal bounds.",
                "status": "Normal",
                "delivery_status": "Logged",
                "is_read": is_read
            })

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
        status_label = "Active" if is_active else "Resolved"

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
            "critical_count": critical_count,
            "warning_count": warning_count,
            "resolved_count": resolved_count,
            "unread_notifications": unread_notifications,
            "dispatch_stats": {
                "sent": sent_count,
                "delivered": delivered_count,
                "failed": failed_count,
            }
        }
    })


@app.route("/historical/export")
@role_required("Client")
def export_historical_data():
    target_date = request.args.get("date", "all").strip()
    target_status = request.args.get("status", "all").strip().lower()
    export_format = request.args.get("format", "xlsx").strip().lower()
    if export_format not in ("xlsx", "csv"):
        export_format = "xlsx"

    try:
        readings = db.session.execute(
            select(sensor_readings).order_by(sensor_readings.c.date.asc())
        ).mappings().all()
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
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    return render_template("dashboard.html", user=user, greeting=greeting)


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

    if not user_name or len(user_name) > 80:
        flash("Enter a name between 1 and 80 characters.", "error")
    elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 255:
        flash("Enter a valid email address.", "error")
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

    if not user_name or len(user_name) > 80:
        flash("Enter a name between 1 and 80 characters.", "error")
    elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 255:
        flash("Enter a valid email address.", "error")
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
        user.user_name = user_name
        user.email = email
        user.role = role
        user.status = status
        if new_password:
            user.set_password(new_password)
        try:
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

    except SQLAlchemyError:
        db.session.rollback()

        total_users = 0
        active_users = 0
        inactive_users = 0
        role_summary = []
        recent_activities = []
        system_online = False

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        role_summary=role_summary,
        recent_activities=recent_activities,
        system_online=system_online,
    )


@app.route("/admin/telemetry")
@role_required("Admin")
def admin_telemetry():
    try:
        readings_query = db.session.execute(
            select(sensor_readings).order_by(sensor_readings.c.date.desc())
        ).mappings().all()

        total_readings = len(readings_query)
        recent_serialized = [
            serialize_sensor_reading(r) for r in readings_query[:100]
        ]
        latest_reading = recent_serialized[0] if recent_serialized else None

        # Check if gateway is online (reading within last 2 hours or readings exist)
        gateway_online = False
        if readings_query:
            try:
                latest_dt = parse_reading_datetime(readings_query[0])
                if datetime.now() - latest_dt < timedelta(hours=2):
                    gateway_online = True
            except Exception:
                gateway_online = total_readings > 0
        elif total_readings > 0:
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
        gateway_online = False
        optimal_count = warning_count = critical_count = 0
        optimal_pct = warning_pct = critical_pct = 0.0

    return render_template(
        "admin_telemetry.html",
        gateway_online=gateway_online,
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
            writer.writerow([
                s.get("recorded_at", ""),
                s.get("temperature", ""),
                s.get("ph", ""),
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
        temp = float(temp_raw)
        ph = float(ph_raw)
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
            details=f"Admin ingested test telemetry: Temp={temp}°C, pH={ph}, ML Status={overall_status}.",
            user_email=session.get("user_id"),
            role="Admin",
        )
        flash(f"Test telemetry ingested: {temp}°C, pH {ph} classified as {overall_status}.", "success")
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

        logs = query.order_by(ActivityLog.timestamp.desc()).all()

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
            io.BytesIO(output.getvalue().encode("utf-8")),
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

        session["login_csrf_token"] = secrets.token_urlsafe(32)

    else:
        expected_token = session.get("login_csrf_token", "")
        submitted_token = request.form.get("csrf_token", "")
        user_name = request.form.get("user_name", "").strip()
        password = request.form.get("password", "")

        if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
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

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "GET":
        session["signup_csrf_token"] = secrets.token_urlsafe(32)
    else:
        expected_token = session.get("signup_csrf_token", "")
        submitted_token = request.form.get("csrf_token", "")
        user_name = request.form.get("user_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
            error = "Your sign-up request expired. Please try again."
        elif not user_name or len(user_name) > 80:
            error = "Enter a username between 1 and 80 characters."
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 255:
            error = "Enter a valid email address."
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

        session["signup_csrf_token"] = secrets.token_urlsafe(32)

    return render_template("signup.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    expected_token = session.get("logout_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")
    if not expected_token or not hmac.compare_digest(expected_token, submitted_token):
        return "Invalid logout request.", 400

    user_email = session.get("user_id")
    user_role = session.get("user_role")
    user_name = session.get("user_name")
    if user_email:
        log_activity(
            action="LOGOUT",
            details="User signed out of the system.",
            user_email=user_email,
            user_name=user_name,
            role=user_role,
        )

    session.clear()
    return redirect(url_for("login"))


@app.route("/monitoring")
@role_required("Client")
def monitoring():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    return render_template("monitoring.html", user=user)


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


@app.route("/settings", methods=["GET", "POST"])
@role_required("Client")
def settings():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email)
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    csrf_token = session.setdefault("settings_csrf_token", secrets.token_urlsafe(32))
    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        action = request.form.get("action", "")
        if not hmac.compare_digest(csrf_token, submitted_token):
            flash("Your request expired. Please try again.", "error")
        elif action == "profile":
            user_name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            ntfy_topic = request.form.get("ntfy_topic", "").strip()
            if not user_name or len(user_name) > 80:
                flash("Enter a name between 1 and 80 characters.", "error")
            elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 255:
                flash("Enter a valid email address.", "error")
            elif User.query.filter(User.email != user_email, User.email == email).first():
                flash("An account with that email already exists.", "error")
            elif User.query.filter(User.email != user_email, User.user_name == user_name).first():
                flash("A user with that name already exists.", "error")
            elif ntfy_topic and not is_valid_topic(ntfy_topic):
                flash("Invalid ntfy topic. Use 3-64 characters (letters, numbers, hyphens, and underscores only).", "error")
            else:
                user.user_name = user_name
                user.email = email
                user.ntfy_topic = ntfy_topic
                try:
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
                        role=user.role,
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




def get_latest_sensor_dict():
    try:
        readings = db.session.execute(select(sensor_readings)).mappings().all()
        if not readings:
            return None
        latest = max(readings, key=parse_reading_datetime)
        return {
            "temperature": float(latest["temperature"]),
            "ph": float(latest["ph_level"]),
            "status": str(latest.get("status") or "Optimal"),
            "recorded_at": str(latest["date"])
        }
    except Exception:
        return None


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
        latest = get_latest_sensor_dict()
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


if __name__ == "__main__":
    app.run(debug=True)
