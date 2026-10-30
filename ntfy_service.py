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


def send_water_quality_alert_ntfy(severity, temp, ph, reason=None, topic=None, click_url=None):
    """
    Formats and dispatches a shrimp pond water quality emergency alert via ntfy.sh.
    """
    severity_upper = str(severity).upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    if severity_upper == "CRITICAL":
        priority = 5
        tags = ["rotating_light", "warning", "shrimp"]
        title = f"ShrimpGuard EMERGENCY [{severity_upper}]"
        default_remediation = "Emergency remediation required! Check aeration, heaters, and water treatment immediately."
    elif severity_upper == "WARNING":
        priority = 4
        tags = ["warning", "shrimp"]
        title = f"ShrimpGuard WARNING [{severity_upper}]"
        default_remediation = "Pond conditions in caution range. Monitor closely and adjust water buffers."
    else:
        priority = 3
        tags = ["white_check_mark", "shrimp"]
        title = f"ShrimpGuard Notification [{severity_upper}]"
        default_remediation = "Pond water parameters within safe operational thresholds."

    action = reason or default_remediation

    body_message = (
        f"Penaeus vannamei Pond Alert\n"
        f"• Temperature: {temp:.1f} °C (Optimal: 28.0–32.0 °C)\n"
        f"• pH Level: {ph:.2f} (Optimal: 7.50–8.50)\n"
        f"• ML Status: {severity_upper}\n\n"
        f"Action Required:\n{action}\n\n"
        f"Logged at: {timestamp}"
    )

    return send_ntfy_notification(
        message=body_message,
        title=title,
        topic=topic,
        priority=priority,
        tags=tags,
        click_url=click_url
    )
