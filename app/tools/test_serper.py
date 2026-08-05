# test_serper.py
import requests
import os 
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("SERPAPI_API_KEY")

response = requests.post(
    "https://google.serper.dev/shopping",
    headers={
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json",
    },
    json={"q": "iPhone 16 Pro", "gl": "eg", "hl": "ar", "num": 5},
)

print("Status:", response.status_code)
print(response.json())