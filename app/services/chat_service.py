from app.models.models import ChatRequest, ChatResponse, Message
from app.repositories.chat_repository import (
    create_session,
    add_message,
    get_session_messages
)
from datetime import datetime
from typing import Dict

class ChatService:
    async def create_session(self, session_id: str):
        await create_session(session_id)

    async def process_chat(self, req: ChatRequest) -> ChatResponse:
        await self.create_session(req.session_id)
        await add_message(req.session_id, "user", req.message)

        bot_response = "Você disse: " + req.message
        await add_message(req.session_id, "bot", bot_response)

        msgs = await get_session_messages(req.session_id)
        return ChatResponse(
            session_id=req.session_id,
            messages=[Message(**m) for m in msgs]
        )

    async def process_webhook(self, body: dict) -> Dict[str, str]:
        query_text = body.get("queryResult", {}).get("queryText", "")
        if "olá" in query_text.lower():
            response = "Oi! Seja bem-vindo!"
        else:
            response = "Ainda estou aprendendo :)"
        return {"fulfillmentText": response}
