import os, sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "").strip()
base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
model = os.getenv("OPENAI_MODEL", "").strip()

client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0, max_retries=0)

try:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Explain in 15 words why water temperature affects Penaeus vannamei feed conversion."}],
        max_tokens=60
    )
    print("SUCCESS! Content:", resp.choices[0].message.content)
except Exception as e:
    print("Error type:", type(e))
    print("Error details:", repr(e))
    if hasattr(e, "response"):
        print("Response text:", getattr(e.response, "text", ""))

