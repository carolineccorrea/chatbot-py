# Dockerfile

# 1) Escolhe uma imagem Python slim
FROM python:3.13-slim

# 2) Evita prompts interativos de apt
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# 3) Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copia o restante da aplicação
COPY . .

# 5) Expõe a porta que o Uvicorn vai usar
EXPOSE 8080

# 6) Comando padrão para iniciar sua API FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
