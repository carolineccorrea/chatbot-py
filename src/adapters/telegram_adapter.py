# src/interfaces/http/adapters/telegram_adapter.py
import os
import httpx
from src.adapters.base_adapter import BaseAdapter
from src.domain.models.models import Message

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL    = f"https://api.telegram.org/bot{BOT_TOKEN}"

class TelegramAdapter(BaseAdapter):
    async def parse_request(self, payload: dict) -> Message:
        chat_id = payload["message"]["chat"]["id"]
        text    = payload["message"]["text"]
        return Message(
            channel="telegram",
            user_id=str(chat_id),
            sender="user",
            text=text,
            metadata=payload.get("metadata", {})
        )

    async def send_response(self, message: Message, reply_text: str) -> None:
        await httpx.post(
            f"{API_URL}/sendMessage",
            json={"chat_id": message.user_id, "text": reply_text}
        )
