# Use a slim Python base image
FROM python:3.13-slim

# Evita prompts interativos durante instalações
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema para compilar faiss-cpu
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    swig \
    libopenblas-dev \
    liblapack-dev \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

# Cria e define o diretório de trabalho
WORKDIR /app

# Copia só o requirements para aproveitar cache
COPY requirements.txt .

# Atualiza pip e instala dependências Python
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta usada pelo app
ENV PORT=8080

# Comando padrão de inicialização
CMD ["python", "main.py"]
