# src/api/controllers/chat_controller.py

import uuid
import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.domain.models.models import ChatRequest, ChatResponse
from src.domain.usecases.create_session_use_case import CreateSessionUseCase
from src.domain.usecases.process_chat_use_case import ProcessChatUseCase
from src.infra.repositories.mongo_session_repository import MongoSessionRepository

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/start-session")
@limiter.limit("10/minute")
async def start_session(request: Request, req: ChatRequest):
    try:
        session_id = str(uuid.uuid4())
        uc = CreateSessionUseCase(MongoSessionRepository())
        await uc.execute(req.company_id, session_id)
        return {"company_id": req.company_id, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, req: ChatRequest):
    try:
        uc = ProcessChatUseCase(MongoSessionRepository())
        history = await uc.execute(req.company_id, req.session_id, req.message)
        return ChatResponse(
            company_id=req.company_id,
            session_id=req.session_id,
            messages=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
@limiter.limit("10/minute")
async def webhook(request: Request):
    try:
        body = await request.json()
        return {"status": "ok", "received": body}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget", response_class=HTMLResponse)
async def get_chat_widget():
    file_path = os.path.join("static", "chatbot_widget.html")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()