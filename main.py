import time
import logging

from bot.config import ALLOWED_CHAT_ID
from bot import telegram
from bot.router import route

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

offset = 0

log.info("Ghost Runner started. Authorised chat: %d", ALLOWED_CHAT_ID)

while True:
    try:
        updates = telegram.get_updates(offset)

        for update in updates:
            offset = update["update_id"] + 1

            message = update.get("message")
            if not message:
                continue

            text = message.get("text")
            if not text:
                continue

            chat_id: int = message["chat"]["id"]

            # ── AUTH GATE ─────────────────────────────────────────────────
            if chat_id != ALLOWED_CHAT_ID:
                log.warning("Blocked message from unknown chat_id=%d", chat_id)
                continue  # silent — no reply
            # ─────────────────────────────────────────────────────────────

            reply = route(text)
            telegram.send_message(chat_id, reply)
            log.info("chat=%d | in=%r | out=%r", chat_id, text, reply)

    except Exception as exc:
        # Network blip, Telegram hiccup, etc. — log and keep looping.
        log.error("Poll error (will retry in 5 s): %s", exc)
        time.sleep(5)
        continue

    time.sleep(1)
