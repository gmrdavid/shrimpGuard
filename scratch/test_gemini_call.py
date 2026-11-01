import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "").strip()
base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
model = os.getenv("OPENAI_MODEL", "gemini-1.5-flash").strip()

print(f"Testing model: {model}")
print(f"Base URL: {base_url}")

client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0, max_retries=0)

for test_model in [model, "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]:
    try:
        print(f"\nAttempting call with model: {test_model}...")
        resp = client.chat.completions.create(
            model=test_model,
            messages=[{"role": "user", "content": "Reply with only 'GEMINI_OK'"}],
            max_tokens=10
        )
        print(f"SUCCESS with {test_model}! Content: {resp.choices[0].message.content.strip()}")
        break
    except Exception as e:
        print(f"Failed with {test_model}: {e}")

