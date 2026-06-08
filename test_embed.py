import os
from dotenv import load_dotenv
import httpx
import json

load_dotenv()

# Test with raw httpx to see exactly what langchain sends
url = f"{os.environ['DEEPSEEK_API_BASE']}/embeddings"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['DEEPSEEK_API_KEY']}",
}

# Standard OpenAI format
payload_standard = {
    "model": "text-embedding-v3",
    "input": ["hello world"],
}

print("=== Test 1: Standard OpenAI format ===")
resp = httpx.post(url, headers=headers, json=payload_standard)
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text[:500]}")
