import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "").strip()
base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None

client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0, max_retries=0)

models_to_test = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro",
    "gemini-2.5-flash",
    "gemini-1.0-pro"
]

for m in models_to_test:
    try:
        resp = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        print(f"SUCCESS with {m}! Content: {resp.choices[0].message.content}")
    except Exception as e:
        status_code = getattr(e, 'status_code', None)
        print(f"Failed with {m}: code={status_code}")

