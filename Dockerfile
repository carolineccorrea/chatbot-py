# Use a slim Python base image
FROM python:3.13-slim

# Prevent interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages required to build faiss-cpu
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    swig \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy only requirements.txt first to leverage Docker layer cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application code
COPY . .

# Expose the application port
ENV PORT=8080

# Default command to run the application
CMD ["python", "main.py"]
