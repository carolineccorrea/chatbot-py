FROM python:3.10-slim

# Cria diretório app
WORKDIR /app

# Copia arquivos
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Define a porta do app
ENV PORT=8080

# Comando para rodar o app (ex: main.py com app.run(host='0.0.0.0'))
CMD ["python", "main.py"]
