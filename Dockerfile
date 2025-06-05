# ───────────────────────────────────────────────────────────
# 1) Imagem base: Python 3.13 slim
# ───────────────────────────────────────────────────────────
FROM python:3.13-slim

# ───────────────────────────────────────────────────────────
# 2) Variáveis de ambiente
# ───────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# ───────────────────────────────────────────────────────────
# 3) Instala dependências de SO para compilar pacotes e Mongo
# ───────────────────────────────────────────────────────────
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      gfortran \
      libopenblas-dev \
      libssl-dev \
      curl \
 && rm -rf /var/lib/apt/lists/*

# ───────────────────────────────────────────────────────────
# 4) Copia e instala dependências Python
# ───────────────────────────────────────────────────────────
COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ───────────────────────────────────────────────────────────
# 5) Copia todo o código fonte
# ───────────────────────────────────────────────────────────
COPY . .

# ───────────────────────────────────────────────────────────
# 6) Expõe a porta que o FastAPI usará
# ───────────────────────────────────────────────────────────
EXPOSE 8080

# ───────────────────────────────────────────────────────────
# 7) Healthcheck HTTP para /health
# ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# ───────────────────────────────────────────────────────────
# 8) Comando de inicialização
# ───────────────────────────────────────────────────────────
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port $PORT --log-level info"]
