# Use uma imagem base leve de Python
FROM python:3.13-slim

# Evita prompts interativos e ativa saída de log em tempo real
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Cria o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema (necessárias p/ faiss, OpenBLAS etc)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      gfortran \
      libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# Copia só o requirements pra usar cache de camadas
COPY requirements.txt .

# Instala as libs Python
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do código
COPY . .

# Expõe a porta usada pelo Cloud Run
EXPOSE 8080

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
