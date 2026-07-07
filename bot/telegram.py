import httpx
from bot.config import TOKEN

API = f"https://api.telegram.org/bot{TOKEN}"

def get_updates(offset: int) -> list[dict]:
    """Poll for new updates starting from offset."""
    resp = httpx.get(
        f"{API}/getUpdates",
        params={"offset": offset, "timeout": 10},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["result"]


def send_message(chat_id: int, text: str) -> None:
    """Send a text message to chat_id."""
    httpx.post(
        f"{API}/sendMessage",
        params={"chat_id": chat_id, "text": text},
        timeout=10,
    )
