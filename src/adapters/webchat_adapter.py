# src/interfaces/websocket/webchat_adapter.py
from fastapi import WebSocket
from src.adapters.base_adapter import BaseAdapter
from src.domain.models.models import Message

connections: dict[str, WebSocket] = {}

class WebchatAdapter(BaseAdapter):
    async def parse_request(self, payload: dict) -> Message:
        return Message(
            channel="webchat",
            user_id=payload["user_id"],
            sender="user",
            text=payload["text"],
            metadata=payload.get("metadata", {})
        )

    async def send_response(self, message: Message, reply_text: str) -> None:
        ws = connections.get(message.user_id)
        if ws:
            await ws.send_text(reply_text)
