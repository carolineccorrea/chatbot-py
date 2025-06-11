# Use a imagem oficial Python
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY src/ ./src/

# Define a porta para o Cloud Run
ENV PORT=8080
EXPOSE 8080

# Comando de startup
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
