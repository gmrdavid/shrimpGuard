import hmac
import io
import math
import os
import re
import secrets
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from xml.sax.saxutils import escape

from flask import Flask, flash, has_request_context, jsonify, redirect, render_template, request, send_file, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, select, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from recommendations import RecommendationModelError, predict_recommendation

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
    if session.get("user_id") is None:
        return {"logout_csrf_token": ""}
    return {
        "logout_csrf_token": session.setdefault(
            "logout_csrf_token", secrets.token_urlsafe(32)
        )
    }


def serialize_sensor_reading(reading):
    return {
        "temperature": reading["temperature"],
        "ph": reading["ph_level"],
        "recorded_at": reading["date"],
        "status": reading["status"],
    }


def role_required(required_role):
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user_id = session.get("user_id")
            if user_id is None:
                return redirect(url_for("login"))

            try:
                user = db.session.get(User, user_id)
            except SQLAlchemyError:
                db.session.rollback()
                return "Authentication service is temporarily unavailable. Please retry.", 503

            if user is None:
                session.clear()
                return redirect(url_for("login"))

            actual_role = user.role.strip().casefold()
            if actual_role != required_role.casefold():
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
        recorded_at = (
            datetime.fromisoformat(payload["recorded_at"])
            if payload.get("recorded_at")
            else datetime.now()
        )
    except (TypeError, ValueError):
        return jsonify({"error": "Reading values must be valid numbers and date."}), 400
    if not math.isfinite(temperature) or not math.isfinite(ph):
        return jsonify({"error": "Reading values must be finite numbers."}), 400

    status = (
        "Critical"
        if temperature < 26 or temperature > 32 or ph < 7.5 or ph > 8.5
        else "Normal"
    )
    try:
        db.session.execute(
            insert(sensor_readings).values(
                ph_level=ph,
                temperature=temperature,
                date=recorded_at.isoformat(),
                status=status,
            )
        )
        db.session.commit()
        return jsonify(
            {
                "temperature": temperature,
                "ph": ph,
                "recorded_at": recorded_at.isoformat(),
                "status": status,
            }
        ), 201
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to save sensor reading.")
        return jsonify({"error": "Unable to save sensor reading."}), 503


@app.route("/api/readings/latest")
@role_required("Client")
def latest_reading():
    try:
        reading = db.session.execute(
            select(sensor_readings)
            .order_by(sensor_readings.c.date.desc())
            .limit(1)
        ).mappings().first()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load the latest sensor reading.")
        return jsonify({"error": "Unable to load sensor readings."}), 503
    if not reading:
        return jsonify(None)
    return jsonify(serialize_sensor_reading(reading))


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
            .order_by(sensor_readings.c.date.desc())
        ).mappings().all()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load sensor reading history.")
        return jsonify({"error": "Unable to load sensor readings."}), 503
    return jsonify([serialize_sensor_reading(reading) for reading in reversed(readings)])


@app.route("/historical/export")
@role_required("Client")
def export_historical_data():
    try:
        readings = db.session.execute(
            select(sensor_readings).order_by(sensor_readings.c.date.asc())
        ).mappings().all()
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("Unable to load sensor readings for export.")
        return jsonify({"error": "Unable to load sensor readings for export."}), 503

    rows = [
        ("Date", "Temperature (°C)", "pH", "Status"),
    ]
    for reading in readings:
        try:
            recorded_at = datetime.fromisoformat(reading["date"])
            temperature = float(reading["temperature"])
            ph = float(reading["ph_level"])
        except (TypeError, ValueError):
            app.logger.exception("A stored sensor reading has invalid values.")
            return jsonify({"error": "A stored sensor reading has invalid values."}), 500
        if not math.isfinite(temperature) or not math.isfinite(ph):
            app.logger.error("A stored sensor reading contains non-finite values.")
            return jsonify({"error": "A stored sensor reading contains invalid numeric values."}), 500
        status = (
            "Critical"
            if temperature < 26
            or temperature > 32
            or ph < 7.5
            or ph > 8.5
            else "Normal"
        )
        if reading["status"].strip().casefold() == "demo":
            status = f"Demo - {status}"
        rows.append(
            (
                recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
                format(temperature, ".15g"),
                format(ph, ".15g"),
                status,
            )
        )

    def text_cell(reference, value):
        return (
            f'<c r="{reference}" t="inlineStr"><is><t xml:space="preserve">'
            f"{escape(str(value))}</t></is></c>"
        )

    worksheet_rows = []
    for row_number, row in enumerate(rows, start=1):
        cells = [
            text_cell(f"A{row_number}", row[0]),
            text_cell(f"B{row_number}", row[1]) if row_number == 1 else f'<c r="B{row_number}"><v>{row[1]}</v></c>',
            text_cell(f"C{row_number}", row[2]) if row_number == 1 else f'<c r="C{row_number}"><v>{row[2]}</v></c>',
            text_cell(f"D{row_number}", row[3]),
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
        download_name="shrimpguard-historical-data.xlsx",
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

    if not user_name or len(user_name) > 80:
        flash("Enter a name between 1 and 80 characters.", "error")
    elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 255:
        flash("Enter a valid email address.", "error")
    elif role not in {"Admin", "Client"}:
        flash("Choose Admin or Client as the role.", "error")
    elif status not in {"Active", "Inactive"}:
        flash("Choose Active or Inactive as the status.", "error")
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
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("The user could not be updated. Please try again.", "error")
        else:
            if session.get("user_id") == current_email:
                session["user_id"] = email
            session["admin_csrf_token"] = secrets.token_urlsafe(32)
            log_activity(
                action="USER_EDIT",
                details=f"Updated account {user_name} ({email}) - Role: {role}, Status: {status}.",
                user_email=session.get("user_id"),
                role="Admin",
            )
            flash("User updated successfully.", "success")

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
                .limit(20)
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
    return render_template("monitoring.html")


@app.route("/historical")
@role_required("Client")
def historical():
    return render_template("historical.html")


@app.route("/alerts")
@role_required("Client")
def alerts():
    return render_template("alerts.html")


@app.route("/analytics")
@role_required("Client")
def analytics():
    return render_template("analytics.html")


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
            if not user_name or len(user_name) > 80:
                flash("Enter a name between 1 and 80 characters.", "error")
            elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 255:
                flash("Enter a valid email address.", "error")
            elif User.query.filter(User.email != user_email, User.email == email).first():
                flash("An account with that email already exists.", "error")
            elif User.query.filter(User.email != user_email, User.user_name == user_name).first():
                flash("A user with that name already exists.", "error")
            else:
                user.user_name = user_name
                user.email = email
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


if __name__ == "__main__":
    app.run(debug=True)