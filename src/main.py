# src/main.py

import os
import json
import logging
import asyncio

from dotenv import load_dotenv
import httpx

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse

from src.registry import load_adapters
from src.infra.db.mongo.db_config import client, MONGO_URI
from src.api.repositories.mongo_session_repository import MongoSessionRepository
from src.domain.usecases.create_session_use_case import CreateSessionUseCase
from src.domain.usecases.process_chat_use_case import ProcessChatUseCase
from src.api.controllers.chat_controller import router as chat_router

# Carrega variáveis de ambiente
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis de ambiente obrigatórias
BOT_TOKEN        = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL      = os.getenv("TELEGRAM_WEBHOOK_URL")
MONGODB_URI      = os.getenv("MONGODB_URI")
MONGODB_DB_NAME  = os.getenv("MONGODB_DB_NAME", "")
PORT             = int(os.getenv("PORT", 8000))

if not BOT_TOKEN:
    raise RuntimeError("💥 TELEGRAM_BOT_TOKEN não definido")
if not WEBHOOK_URL:
    raise RuntimeError("💥 TELEGRAM_WEBHOOK_URL não definido")
if not MONGODB_URI:
    raise RuntimeError("💥 MONGODB_URI não definido")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Instancia FastAPI
app = FastAPI()

# 1) Health-check
@app.get("/health")
async def health_check():
    return {"status": "ok", "port": PORT}

# 2) Inclui rotas REST sob /api
app.include_router(chat_router, prefix="/api")

# 3) Serve estáticos, favicon e widget
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")

@app.get("/widget")
async def get_widget():
    path = os.path.join("static", "chatbot_widget.html")
    if not os.path.isfile(path):
        return FileResponse(path="static/404.html", status_code=404)
    return FileResponse(path, media_type="text/html")

# 4) Startup: conecta no MongoDB em background
@app.on_event("startup")
async def startup_db():
    async def try_connect():
        try:
            await client.server_info()
            logger.info(f"🔗 Conectado ao MongoDB em {MONGO_URI}, banco: {MONGODB_DB_NAME}")
        except Exception as e:
            logger.error(f"❌ Falha ao conectar no MongoDB: {e}")

    asyncio.create_task(try_connect())

# Telegram
@app.on_event("startup")
async def configure_webhook():
    async with httpx.AsyncClient() as http_client:
        resp_del = await http_client.get(
            f"{API_URL}/deleteWebhook",
            params={"drop_pending_updates": True}
        )
        logger.info("🗑 deleteWebhook: %s", resp_del.json())

        resp_set = await http_client.get(
            f"{API_URL}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        logger.info("📥 setWebhook: %s", resp_set.json())


@app.on_event("shutdown")
async def shutdown_db():
    client.close()
    logger.info("🔒 Conexão com MongoDB encerrada")


adapters   = load_adapters()
repository = MongoSessionRepository()
create_uc  = CreateSessionUseCase(repository)
process_uc = ProcessChatUseCase(repository)

# Webhook universal
@app.post("/api/webhook/{channel}")
async def universal_webhook(channel: str, request: Request):
    # 8.1) Lê JSON e trata UnicodeDecodeError
    try:
        payload = await request.json()
    except UnicodeDecodeError:
        raw = await request.body()
        try:
            payload = json.loads(raw.decode("latin-1"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")

    if channel not in adapters:
        raise HTTPException(status_code=400, detail="canal não suportado")
    adapter = adapters[channel]

    msg = await adapter.parse_request(payload)

    if channel == "telegram":
        company_id = "default"
        session_id = msg.user_id
    else:
        company_id = msg.metadata.get("company_id")
        session_id = msg.metadata.get("session_id")

    if not (company_id and session_id):
        raise HTTPException(
            status_code=400,
            detail="metadata missing company_id or session_id"
        )

    await create_uc.execute(company_id, session_id)
    history = await process_uc.execute(company_id, session_id, msg)

    last_bot = next((m for m in reversed(history) if m.sender == "bot"), None)
    if last_bot:
        await adapter.send_response(msg, last_bot.text)

    logger.info(f"📬 [{channel}] company={company_id} session={session_id} messages={len(history)}")
    return {"status": "ok"}

# WebSocket para webchat
@app.websocket("/ws/{company_id}/{session_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, company_id: str, session_id: str, user_id: str):
    await websocket.accept()
    ws_adapter = adapters.get("webchat")
    ws_adapter.connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            data.setdefault("metadata", {}).update({
                "company_id": company_id,
                "session_id": session_id
            })
            msg = await ws_adapter.parse_request(data)
            history = await process_uc.execute(company_id, session_id, msg)
            last_bot = next((m for m in reversed(history) if m.sender == "bot"), None)
            if last_bot:
                await ws_adapter.send_response(msg, last_bot.text)
            logger.info(
                f"🕸️ [websocket] company={company_id} session={session_id} user={user_id} text={msg.text}"
            )
    except WebSocketDisconnect:
        ws_adapter.connections.pop(user_id, None)
        logger.info(f"🚪 WebSocket desconectado: {user_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, reload=True)
