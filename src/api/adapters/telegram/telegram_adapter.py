# src/api/adapters/telegram/telegram_adapter.py

import os
import logging
import httpx
from src.api.adapters.base_adapter import BaseAdapter
from src.domain.models.models import Message

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("💥 TELEGRAM_BOT_TOKEN não definido")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

class TelegramAdapter(BaseAdapter):
    async def parse_request(self, payload: dict) -> Message:
        msg = payload.get("message", {})
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        logger.info("➡️ Mensagem recebida no chat_id: %s", chat_id)
        text = msg.get("text", "") or ""
        phone_number = None
        if "contact" in msg:
            phone_number = msg["contact"].get("phone_number")
        return Message(
            channel="telegram",
            user_id=str(chat_id),
            sender="user",
            text=text,
            phone_number=phone_number,
            metadata=payload.get("metadata", {})
        )

    async def send_response(self, message: Message, reply_text: str) -> None:
        """
        Envia resposta via Telegram API. Em caso de erro de requisição,
        registra detalhes no log ao invés de lançar.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{API_URL}/sendMessage",
                    json={
                        "chat_id": message.user_id,
                        "text": reply_text
                    }
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Loga detalhes do erro
                err_json = None
                try:
                    err_json = e.response.json()
                except Exception:
                    err_json = e.response.text
                logger.error(
                    "❌ Erro ao enviar mensagem para Telegram: %s, status: %s, response: %s",
                    e.request.url, e.response.status_code, err_json
                )
