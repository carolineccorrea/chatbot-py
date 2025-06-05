FROM python:3.13-slim

# ================================
# 1) Variáveis de ambiente padrão
# ================================
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# ================================
# 2) Instala dependências de SO
# ================================
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      gfortran \
      libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# ================================
# 3) Copia e instala requirements
# ================================
COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ================================
# 4) Copia o restante da aplicação
# ================================
COPY . .

# ================================
# 5) Expondo a porta padrão
# ================================
EXPOSE 8080

# ================================
# 6) (Opcional) HEALTHCHECK
#
#    Verifica a rota /health a cada 30s, 
#    marcada como falha se retornar código ≠ 2xx.
# ================================
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget -qO- http://localhost:${PORT}/health || exit 1

# ================================
# <<< aqui!  Comando de inicialização
#
#    Este CMD indica ao Docker “como” iniciar a 
#    aplicação quando o container subir.
#    No caso, usamos uvicorn para servir a FastAPI.
# ================================
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port $PORT"]

