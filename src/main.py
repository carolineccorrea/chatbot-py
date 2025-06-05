import os
import logging
import asyncio

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse

from src.infra.db.mongo.db_config import client, MONGO_URI, DB_NAME
from src.registry import load_adapters
from src.infra.repositories.mongo_session_repository import MongoSessionRepository
from src.domain.usecases.create_session_use_case import CreateSessionUseCase
from src.domain.usecases.process_chat_use_case import ProcessChatUseCase
from src.api.controllers.chat_controller import router as chat_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ---------------------------------------------------
# 1) Endpoint mínimo de health (resposta imediata)
# ---------------------------------------------------
@app.get("/health")
async def health_check():
    """
    Retorna {"status": "ok", "port": ...} para checagem de readiness.
    """
    return {"status": "ok", "port": os.getenv("PORT", "desconhecido")}


# ---------------------------------------------------
# 2) Inclui rotas do chat_controller sob o prefixo /api
# ---------------------------------------------------
app.include_router(chat_router, prefix="/api")

# ---------------------------------------------------
# 3) Serve arquivos estáticos da pasta "static"
# ---------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/widget")
async def get_widget():
    caminho = os.path.join("static", "chatbot_widget.html")
    if not os.path.isfile(caminho):
        return FileResponse(path="static/404.html", status_code=404)
    return FileResponse(caminho, media_type="text/html")


# ---------------------------------------------------
# 4) Startup event: dispara conexão ao Mongo em background
# ---------------------------------------------------
@app.on_event("startup")
async def startup_db():
    """
    Em vez de usar 'await client.server_info()' de forma síncrona,
    disparamos uma tarefa em background para não bloquear a abertura da porta.
    """
    async def try_connect():
        try:
            await client.server_info()  # espera até 5s, pois definimos serverSelectionTimeoutMS=5000
            logger.info(f"🔗 Conectado ao MongoDB em {MONGO_URI}, banco: {DB_NAME}")
        except Exception as e:
            logger.error(f"❌ Falha ao conectar no MongoDB (timeout ou outro): {e}")

    # Dispara a checagem sem await, para que o Uvicorn abra porta imediatamente
    asyncio.create_task(try_connect())


# ---------------------------------------------------
# 5) Shutdown event: fecha a conexão do Mongo
# ---------------------------------------------------
@app.on_event("shutdown")
async def shutdown_db():
    client.close()
    logger.info("🔒 Conexão com MongoDB encerrada")


# ---------------------------------------------------
# 6) Inicializa dependências para caso de uso
# ---------------------------------------------------
adapters = load_adapters()
repository = MongoSessionRepository()
create_uc = CreateSessionUseCase(repository)
process_uc = ProcessChatUseCase(repository)


# ---------------------------------------------------
# 7) Webhook universal (HTTP)
# ---------------------------------------------------
@app.post("/api/webhook/{channel}")
async def universal_webhook(channel: str, request: Request):
    if channel not in adapters:
        return {"error": "canal não suportado"}, 400

    payload = await request.json()
    adapter = adapters[channel]

    msg = await adapter.parse_request(payload)
    company_id = msg.metadata.get("company_id")
    session_id = msg.metadata.get("session_id")

    if not (company_id and session_id):
        return {"error": "metadata missing company_id or session_id"}, 400

    # Cria sessão no DB, se ainda não existir
    await create_uc.execute(company_id, session_id)
    history = await process_uc.execute(company_id, session_id, msg)

    last_bot = [m for m in history if m.sender == "bot"][-1]
    await adapter.send_response(msg, last_bot.text)

    logger.info(
        f"📬 [{channel}] company={company_id} session={session_id} messages={len(history)}"
    )
    return {"status": "ok"}


# ---------------------------------------------------
# 8) WebSocket endpoint para "webchat"
# ---------------------------------------------------
@app.websocket("/ws/{company_id}/{session_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    company_id: str,
    session_id: str,
    user_id: str
):
    await websocket.accept()
    adapter = adapters["webchat"]
    adapter.connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            # Garante que a metadata contenha company_id e session_id
            data.setdefault("metadata", {}).update({
                "company_id": company_id,
                "session_id": session_id
            })
            msg = await adapter.parse_request(data)
            history = await process_uc.execute(company_id, session_id, msg)
            last_bot = [m for m in history if m.sender == "bot"][-1]
            await adapter.send_response(msg, last_bot.text)
            logger.info(
                f"🕸️ [websocket] company={company_id} session={session_id} user={user_id} text={msg.text}"
            )
    except WebSocketDisconnect:
        adapter.connections.pop(user_id, None)
        logger.info(f"🚪 WebSocket desconectado: {user_id}")
