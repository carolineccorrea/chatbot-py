# Dockerfile

# 1) Imagem base Python slim
FROM python:3.13-slim

# 2) Variáveis de ambiente
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# 3) Instala ferramentas de compilação + BLAS para NumPy
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# 4) Copia e instala as libs Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copia o código da aplicação
COPY . .

# 6) Expõe a porta para o Cloud Run
EXPOSE 8080

# 7) Inicia o servidor Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
