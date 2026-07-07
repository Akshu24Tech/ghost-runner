import os
from dotenv import load_dotenv

load_dotenv()

TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_CHAT_ID: int = int(os.environ["ALLOWED_CHAT_ID"])
