import os
import re
import secrets
import urllib.request
import urllib.parse
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Topics on ntfy must be ASCII letters, numbers, hyphens, and underscores (3 to 64 chars)
TOPIC_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,64}$")
RESERVED_TOPICS = {"app", "docs", "static", "account", "settings", "login", "api"}


def is_valid_topic(topic):
    """
    Validates that a topic string is safe and conforms to ntfy.sh rules.
    Prevents path traversal, URL manipulation, and collisions with reserved endpoints.
    """
    if not topic or not isinstance(topic, str):
        return False
    topic_clean = topic.strip()
    if not TOPIC_REGEX.match(topic_clean):
        return False
    if topic_clean.lower() in RESERVED_TOPICS:
        return False
    return True


def generate_secure_topic(prefix="sg-pond-"):
    """
    Generates a cryptographically strong, unguessable private topic name.
    This protects privacy on ntfy.sh so unauthorized third parties cannot guess or listen to alerts.
    Example: 'sg-pond-8f4b2a9e1c7d'
    """
    random_hex = secrets.token_hex(8)
    return f"{prefix}{random_hex}"


def get_parameter_status(temp, ph):
    """
    Evaluates individual parameter statuses specifically for Penaeus vannamei culture:
    - Optimal Temperature: 28.0 - 32.0 °C
    - Optimal pH: 7.50 - 8.50
    Returns: (temp_status, ph_status)
    """
    temp_val = float(temp)
    ph_val = float(ph)

    # Temperature per-parameter evaluation
    if temp_val < 25.0:
        temp_status = "Critical (Severely Low)"
    elif temp_val < 28.0:
        temp_status = "Warning (Sub-optimal Low)"
    elif temp_val <= 32.0:
        temp_status = "Optimal (Normal)"
    elif temp_val <= 34.0:
        temp_status = "Warning (Elevated High)"
    else:
        temp_status = "Critical (Severely High)"

    # pH per-parameter evaluation
    if ph_val < 6.50:
        ph_status = "Critical (Acidic Hazard)"
    elif ph_val < 7.50:
        ph_status = "Warning (Slightly Acidic)"
    elif ph_val <= 8.50:
        ph_status = "Optimal (Normal)"
    elif ph_val <= 9.00:
        ph_status = "Warning (Elevated Alkaline)"
    else:
        ph_status = "Critical (Toxic Alkaline Hazard)"

    return temp_status, ph_status


def send_ntfy_notification(
    message,
    title=None,
    topic=None,
    priority="default",
    tags=None,
    click_url=None
):
    """
    Publishes a push notification safely to ntfy.sh (or a self-hosted ntfy instance) using JSON format.
    - message: Body text of the notification
    - title: Optional header title
    - topic: Target topic. If None, falls back to NTFY_DEFAULT_TOPIC from .env
    - priority: 1 (min), 2 (low), 3 (default), 4 (high), 5 (urgent / emergency)
    - tags: List of tags or comma-separated string (e.g. ['warning', 'shrimp'])
    - click_url: Web link opened when the notification is tapped
    """
    base_url = os.getenv("NTFY_SERVER_URL", "https://ntfy.sh").rstrip("/")
    target_topic = (topic or os.getenv("NTFY_DEFAULT_TOPIC", "")).strip()

    if not target_topic:
        return {
            "success": False,
            "status": "Failed",
            "error": "No ntfy topic specified. Please configure your topic in Settings or .env."
        }

    if not is_valid_topic(target_topic):
        return {
            "success": False,
            "status": "Failed",
            "error": "Invalid topic name. Topics may only contain 3-64 letters, numbers, hyphens (-), and underscores (_)."
        }

    # Normalize priority
    priority_map = {
        "urgent": 5,
        "emergency": 5,
        "critical": 5,
        "high": 4,
        "warning": 4,
        "default": 3,
        "normal": 3,
        "low": 2,
        "min": 1
    }
    if isinstance(priority, str):
        prio_num = priority_map.get(priority.lower(), int(priority) if priority.isdigit() and 1 <= int(priority) <= 5 else 3)
    elif isinstance(priority, int) and 1 <= priority <= 5:
        prio_num = priority
    else:
        prio_num = 3

    # Format tags
    tag_list = []
    if tags:
        if isinstance(tags, list):
            tag_list = [str(t).strip() for t in tags if str(t).strip()]
        elif isinstance(tags, str):
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    payload = {
        "topic": target_topic,
        "message": str(message),
        "priority": prio_num,
    }

    if title:
        payload["title"] = str(title)
    if tag_list:
        payload["tags"] = tag_list
    if click_url:
        payload["click"] = str(click_url)

    endpoint = base_url
    json_bytes = json.dumps(payload).encode("utf-8")

    headers = {
        "User-Agent": "ShrimpGuard-Alerts/2.0",
        "Content-Type": "application/json; charset=utf-8",
    }

    # Optional bearer auth for private/self-hosted ntfy instances
    auth_token = os.getenv("NTFY_ACCESS_TOKEN", "").strip()
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        req = urllib.request.Request(endpoint, data=json_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_bytes = resp.read()
            try:
                resp_json = json.loads(resp_bytes.decode("utf-8"))
            except Exception:
                resp_json = {}

            logger.info(f"ntfy notification successfully sent to topic: {target_topic}")
            return {
                "success": True,
                "status": "Delivered",
                "provider": "ntfy.sh",
                "topic": target_topic,
                "server": base_url,
                "response": resp_json
            }
    except Exception as e:
        logger.exception(f"Error publishing ntfy notification to topic '{target_topic}': {e}")
        return {
            "success": False,
            "status": "Failed",
            "provider": "ntfy.sh",
            "topic": target_topic,
            "error": str(e)
        }


def send_water_quality_alert_ntfy(
    severity,
    temp,
    ph,
    reason=None,
    topic=None,
    click_url=None,
    ai_data=None
):
    """
    Formats and dispatches a comprehensive shrimp pond water quality alert via ntfy.sh containing:
    1. Water parameter values (temperature, pH)
    2. Per-parameter status (e.g. Warning (Elevated High), Critical (Acidic Hazard))
    3. Overall status (ML classification: Critical, Warning, Optimal)
    4. AI recommendation (biological diagnosis from OpenAI API)
    5. Actionable solutions (operational instructions from OpenAI API)
    """
    temp_val = float(temp)
    ph_val = float(ph)
    severity_upper = str(severity).upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    # 1. Per-parameter statuses
    temp_status, ph_status = get_parameter_status(temp_val, ph_val)

    # 2. Query AI recommendation & actionable solutions if not passed
    if ai_data is None:
        try:
            from recommendations import predict_recommendation
            ai_data = predict_recommendation(temp_val, ph_val)
        except Exception as exc:
            logger.warning(f"Unable to load AI recommendation: {exc}")
            ai_data = None

    if ai_data:
        ai_recommendation = ai_data.get("recommendation", "").strip()
        solutions_list = ai_data.get("actionable_solutions", [])
        if not solutions_list and ai_data.get("actionable_solution"):
            solutions_list = [ai_data.get("actionable_solution")]
        ai_source = ai_data.get("source", "OpenAI API")
    else:
        ai_recommendation = reason or "Pond conditions require continued observation and standard monitoring."
        solutions_list = ["Inspect mechanical aerators and monitor pH and dissolved oxygen."]
        ai_source = "ShrimpGuard Engine"

    # Priority and Tags
    if severity_upper == "CRITICAL":
        priority = 5
        tags = ["rotating_light", "warning", "shrimp"]
        title = f"🚨 ShrimpGuard EMERGENCY [{severity_upper}]"
    elif severity_upper == "WARNING":
        priority = 4
        tags = ["warning", "shrimp"]
        title = f"⚠️ ShrimpGuard WARNING [{severity_upper}]"
    else:
        priority = 3
        tags = ["white_check_mark", "shrimp"]
        title = f"ℹ️ ShrimpGuard Notification [{severity_upper}]"

    # Format numbered actionable solutions (up to 4 key actions)
    formatted_actions = []
    for i, act in enumerate(solutions_list[:4], 1):
        formatted_actions.append(f"{i}. {act}")
    actions_text = "\n".join(formatted_actions) if formatted_actions else "1. Continue routine pond monitoring."

    # Build comprehensive alert message
    body_message = (
        f"🦐 Penaeus vannamei Pond Health Report\n\n"
        f"📊 WATER PARAMETERS & STATUS:\n"
        f"• Temperature: {temp_val:.1f} °C — {temp_status} [Optimal: 28.0–32.0 °C]\n"
        f"• pH Level: {ph_val:.2f} — {ph_status} [Optimal: 7.50–8.50]\n"
        f"• Overall Status: {severity_upper} (DecisionTree ML)\n\n"
        f"🤖 AI RECOMMENDATION ({ai_source}):\n"
        f"{ai_recommendation}\n\n"
        f"🛠️ ACTIONABLE SOLUTIONS:\n"
        f"{actions_text}\n\n"
        f"⏱️ Logged at: {timestamp}"
    )

    return send_ntfy_notification(
        message=body_message,
        title=title,
        topic=topic,
        priority=priority,
        tags=tags,
        click_url=click_url
    )
