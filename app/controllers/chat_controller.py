from app.models.models import ChatRequest, ChatResponse, Message
from app.services.chat_service import ChatService
from typing import Dict

chat_service = ChatService()

async def handle_chat(req: ChatRequest) -> ChatResponse:
    return await chat_service.process_chat(req)

async def handle_start_session() -> Dict[str, str]:
    import uuid
    session_id = str(uuid.uuid4())
    await chat_service.create_session(session_id)
    return {"session_id": session_id}

async def handle_webhook(body: dict) -> Dict[str, str]:
    return await chat_service.process_webhook(body)
