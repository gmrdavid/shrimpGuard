import jinja2
import os

template_path = 'templates'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))

try:
    template = env.get_template('devices.html')
    print("Jinja2 compilation SUCCESSFUL!")
except Exception as e:
    print(f"Jinja2 compilation ERROR: {e}")
