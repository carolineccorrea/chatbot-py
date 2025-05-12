# Use um slim Python base image
FROM python:3.13-slim

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instala os pré-requisitos de build + Faiss headers
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    swig \
    build-essential \
    libfaiss-dev \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# Cria e define diretório de trabalho
WORKDIR /app

# Copia o requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY . .

# Expõe a porta usada pelo FastAPI/uvicorn
ENV PORT=8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

#CMD ["python", "main.py"]
