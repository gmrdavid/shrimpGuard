import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "").strip()
base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
model = os.getenv("OPENAI_MODEL", "").strip()

client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0, max_retries=0)

print(f"Calling model: '{model}'")
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Hello, please answer with one sentence: what is Penaeus vannamei?"}],
)
print("Response choices:", resp.choices)
print("Message:", resp.choices[0].message)
print("Content:", resp.choices[0].message.content)

