with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update context processor
old_cp = """@app.context_processor
def inject_logout_csrf_token():
    if session.get("user_id") is None:
        return {"logout_csrf_token": ""}
    return {
        "logout_csrf_token": session.setdefault(
            "logout_csrf_token", secrets.token_urlsafe(32)
        )
    }"""

new_cp = """@app.context_processor
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
    }"""

if old_cp in code:
    code = code.replace(old_cp, new_cp)
    print("Updated context processor")
else:
    print("WARNING: old_cp not found")

# 2. Update export_historical_data
old_export_date = 'recorded_at = datetime.fromisoformat(reading["date"])'
new_export_date = '''recorded_at = parse_reading_datetime(reading)
            if recorded_at == datetime.min:
                try:
                    recorded_at = datetime.fromisoformat(reading["date"])
                except Exception:
                    recorded_at = datetime.now()'''

if old_export_date in code:
    code = code.replace(old_export_date, new_export_date)
    print("Updated export_historical_data date parsing")
else:
    print("WARNING: old_export_date not found")

# 3. Update client routes to pass user and add /calculators
old_client_routes = """@app.route("/monitoring")
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
    return render_template("analytics.html")"""

new_client_routes = """@app.route("/monitoring")
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
    return render_template("calculators.html", user=user)"""

if old_client_routes in code:
    code = code.replace(old_client_routes, new_client_routes)
    print("Updated client routes and added /calculators")
else:
    print("WARNING: old_client_routes not found")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Finished updating app.py")

