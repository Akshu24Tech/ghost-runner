import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"

offset = 0

while True:
    resp = httpx.get(f"{API}/getUpdates", params={"offset": offset})
    updates = resp.json()["result"]

    for update in updates:
        offset = update["update_id"] + 1
        message = update.get("message")
        if not message:
            continue
        text = message.get("text")
        if not text:
            continue
        
        chat_id = message["chat"]["id"]
        httpx.post(f"{API}/sendMessage", params={"chat_id": chat_id, "text": text})
    time.sleep(1)
