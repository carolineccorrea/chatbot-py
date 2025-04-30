from fastapi import APIRouter, Request
from app.models.models import ChatRequest, ChatResponse
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

from app.controllers.chat_controller import (
    handle_chat,
    handle_start_session,
    handle_webhook
)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return await handle_chat(req)

@router.post("/start-session")
async def start_session():
    return await handle_start_session()

@router.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    return await handle_webhook(body)

@router.get("/widget", response_class=HTMLResponse)
async def get_chat_widget():
    # Resolve o caminho relativo à raiz do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "static", "chatbot_widget.html")

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html, status_code=200)