from app.models.models import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

chat_service = ChatService()

async def handle_chat(req: ChatRequest, client_ip: str) -> ChatResponse:
    return await chat_service.process_chat(req, client_ip)

async def handle_start_session():
    import uuid
    session_id = str(uuid.uuid4())
    await chat_service.create_session(session_id)
    return {"session_id": session_id}

async def handle_webhook(body: dict):
    return await chat_service.process_webhook(body)
