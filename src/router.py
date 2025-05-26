from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.api.controllers.chat_controller import handle_chat, handle_start_session
from src.domain.models.models import ChatRequest
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/start-session")
@limiter.limit("10/minute")
async def start_session(request: Request, req: ChatRequest):
    """
    Inicia uma nova sessão para o tenant especificado em req.company_id.
    """
    try:
        return await handle_start_session(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, req: ChatRequest):
    """
    Recebe uma mensagem de chat e devolve o histórico atualizado.
    """
    client_ip = request.client.host
    try:
        return await handle_chat(req, client_ip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget", response_class=HTMLResponse)
async def get_chat_widget():
    """
    Retorna o HTML do widget de chat para inclusão em páginas.
    """
    file_path = os.path.join("static", "chatbot_widget.html")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
