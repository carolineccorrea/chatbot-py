# Dockerfile

# Dockerfile

FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Aqui apontamos para app.main:app e usamos $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
