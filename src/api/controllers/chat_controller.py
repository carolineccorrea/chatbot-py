# src/api/controllers/chat_controller.py

import uuid
import os
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.domain.models.models import ChatRequest, ChatResponse
from src.domain.usecases.create_session_use_case import CreateSessionUseCase
from src.domain.usecases.process_chat_use_case import ProcessChatUseCase
from src.api.repositories.mongo_session_repository import MongoSessionRepository

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

@router.post("/start-session")
@limiter.limit("10/minute")
async def start_session(request: Request, req: ChatRequest):
    """
    Cria uma nova sessão e devolve o session_id gerado.
    """
    try:
        session_id = str(uuid.uuid4())
        repo = MongoSessionRepository()
        await CreateSessionUseCase(repo).execute(req.company_id, session_id)
        return {"company_id": req.company_id, "session_id": session_id}
    except Exception:
        logger.exception("Erro ao atender /start-session")
        raise HTTPException(status_code=500, detail="Erro interno ao criar sessão")

@router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, req: ChatRequest):
    """
    Processa uma mensagem usando o session_date informado no ChatRequest.
    """
    try:
        repo = MongoSessionRepository()
        await CreateSessionUseCase(repo).execute(req.company_id, req.session_id)

        history = await ProcessChatUseCase(repo).execute(
            req.company_id,
            req.session_id,
            req.session_date,
            req.message
        )

        return ChatResponse(
            company_id=req.company_id,
            session_id=req.session_id,
            messages=history
        )
    except Exception:
        logger.exception("Erro ao atender /chat")
        raise HTTPException(status_code=500, detail="Erro interno ao processar o chat")

@router.post("/webhook")
@limiter.limit("10/minute")
async def webhook(request: Request):
    """
    Ponto de entrada para webhooks externos (Telegram, WhatsApp, etc).
    """
    try:
        body = await request.json()
        return {"status": "ok", "received": body}
    except Exception:
        logger.exception("Erro ao atender /webhook")
        raise HTTPException(status_code=500, detail="Erro interno no webhook")

@router.get("/widget", response_class=HTMLResponse)
async def get_chat_widget():
    """
    Serve o widget estático de chat para inclusão em páginas web.
    """
    file_path = os.path.join("static", "chatbot_widget.html")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"Widget não encontrado em {file_path}")
        raise HTTPException(status_code=404, detail="Widget não encontrado")
