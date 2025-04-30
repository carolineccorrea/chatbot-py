from fastapi import FastAPI
from app.router import router  # ou: from app.api.v1.chat_router import router
from app.db.mongo.db_config import mongo_db

app = FastAPI(
    title="Chatbot API",
    version="1.0.0",
    description="API para chatbot com sessão e widget web",
)

app.include_router(router)

# Evento executado ao iniciar o app
@app.on_event("startup")
async def startup():
    try:
        await mongo_db.command("ping")
        print("✅ Conectado ao MongoDB com sucesso!")
    except Exception as e:
        print("❌ Erro ao conectar ao MongoDB:", e)

@app.on_event("shutdown")
async def shutdown():
    print("🛑 Aplicação encerrada.")
