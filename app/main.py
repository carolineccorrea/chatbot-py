import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from app.router import router
from fastapi.responses import FileResponse

app = FastAPI()

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

# Logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# CORS restrito ao domínio do seu site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://carolinecorrea.dev", "http://localhost:8000"],  # adicione localhost para testes locais
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting por IP
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.get("/env.js")
def get_env_js():
    return FileResponse("env.js", media_type="application/javascript")

# Middleware para proteger apenas as rotas sensíveis com API Key
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    protected_paths = ["/chat", "/start-session"]

    if any(request.url.path.startswith(path) for path in protected_paths):
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Acesso não autorizado.")

    return await call_next(request)

# Inclui todas as rotas
app.include_router(router)
