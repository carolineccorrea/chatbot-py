# src/main.py

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from src.registry import load_adapters
from src.infra.repositories.mongo_session_repository import MongoSessionRepository
from src.domain.usecases.create_session_use_case import CreateSessionUseCase
from src.domain.usecases.process_chat_use_case import ProcessChatUseCase
from src.api.controllers.chat_controller import router as chat_router

app = FastAPI()
app.include_router(chat_router, prefix="/api")

# Carrega adapters dinamicamente
adapters   = load_adapters()
repository = MongoSessionRepository()
create_uc  = CreateSessionUseCase(repository)
process_uc = ProcessChatUseCase(repository)

@app.post("/api/webhook/{channel}")
async def universal_webhook(channel: str, request: Request):
    if channel not in adapters:
        return {"error": "canal não suportado"}, 400

    payload = await request.json()
    adapter = adapters[channel]

    # Parse → Message
    msg = await adapter.parse_request(payload)
    company_id = msg.metadata.get("company_id")
    session_id = msg.metadata.get("session_id")

    if not (company_id and session_id):
        return {"error": "metadata missing company_id or session_id"}, 400

    # Cria sessão se necessário
    await create_uc.execute(company_id, session_id)

    # Processa chat
    history = await process_uc.execute(company_id, session_id, msg)

    # Envia apenas a última resposta do bot
    last_bot = [m for m in history if m.sender == "bot"][-1]
    await adapter.send_response(msg, last_bot.text)

    return {"status": "ok"}

@app.websocket("/ws/{company_id}/{session_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, company_id: str, session_id: str, user_id: str):
    await websocket.accept()
    adapter = adapters["webchat"]
    adapter.connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            data.setdefault("metadata", {}).update({
                "company_id": company_id,
                "session_id": session_id
            })

            msg = await adapter.parse_request(data)
            history = await process_uc.execute(company_id, session_id, msg)
            last_bot = [m for m in history if m.sender == "bot"][-1]
            await adapter.send_response(msg, last_bot.text)

    except WebSocketDisconnect:
        adapter.connections.pop(user_id, None)
