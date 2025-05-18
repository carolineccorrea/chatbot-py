from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.controllers.chat_controller import handle_chat, handle_start_session
from src.models.models import ChatRequest
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
load_dotenv()

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/start-session")
@limiter.limit("10/minute")
async def start_session(request: Request):
    return await handle_start_session()

@router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, req: ChatRequest):
    client_ip = request.client.host
    return await handle_chat(req, client_ip)

@router.get("/widget", response_class=HTMLResponse)
async def get_chat_widget():
    file_path = os.path.join("static", "chatbot_widget.html")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
