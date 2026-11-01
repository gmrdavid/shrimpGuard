import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY", "")
base_url = os.getenv("OPENAI_BASE_URL", "")
model = os.getenv("OPENAI_MODEL", "")

print("Key configured:", bool(key and key != "your_openai_api_key_here"))
print("Key length:", len(key))
print("Key prefix:", key[:6] + "..." if len(key) > 6 else "(none)")
print("Base URL:", base_url)
print("Model:", model)

