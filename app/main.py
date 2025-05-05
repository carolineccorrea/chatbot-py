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
from fastapi.staticfiles import StaticFiles

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# CORS restrito ao domínio do seu site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://carolinecorrea.dev", "http://localhost:8000"],
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

# Adicione este bloco para rodar o app corretamente no Cloud Run
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))  # Cloud Run exige que PORT venha da env
    uvicorn.run("main:app", host="0.0.0.0", port=port)
