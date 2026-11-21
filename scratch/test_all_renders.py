from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

mock_data = {
    'session': {'user_id': 1, 'username': 'admin'},
    'total_users': 8,
    'active_users': 6,
    'inactive_users': 2,
    'system_online': True,
    'total_readings': 782,
    'latest_reading': {'temperature': 28.5, 'ph': 10.0, 'status': 'Critical'},
    'gateway_online': False,
    'hw_connected': False,
    'hardware_stream': {'device_id': 'NODE01', 'connected_port': 'COM8'},
    'total_logs': 6226,
    'auth_events': 253,
    'user_mgmt_events': 10,
    'system_settings': {'system_name': 'AERIS-V ShrimpGuard', 'notifications_critical': 'true'},
    'admin_user': {'username': 'admin', 'email': 'admin@shrimpguard.com', 'role': 'Admin', 'ntfy_topic': 'sg-alerts'},
    'admin_csrf_token': 'test_token',
    'users': [
        {'id': 1, 'username': 'admin', 'email': 'admin@shrimpguard.com', 'role': 'Administrator', 'is_active': 1, 'last_login': '2026-05-26 09:30:00'},
        {'id': 2, 'username': 'gliadavid', 'email': 'gliadavid@slsu.edu', 'role': 'Operator', 'is_active': 1, 'last_login': '2026-05-26 08:15:00'}
    ],
    'roles': ['Administrator', 'Operator', 'Viewer'],
    'statuses': ['Active', 'Inactive'],
    'url_for': lambda endpoint, **values: f"/static/{values.get('filename', '')}",
    'get_flashed_messages': lambda **kwargs: []
}

templates_to_test = [
    'admin.html',
    'admin_dashboard.html',
    'admin_telemetry.html',
    'admin_logs.html',
    'admin_settings.html'
]

for tpl_name in templates_to_test:
    try:
        tpl = env.get_template(tpl_name)
        rendered = tpl.render(**mock_data)
        print(f"[OK] {tpl_name}: rendered successfully ({len(rendered)} chars)")
    except Exception as e:
        print(f"[ERROR] {tpl_name}: {e}")
