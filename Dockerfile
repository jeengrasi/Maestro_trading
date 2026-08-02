FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

ENV PYTHONUNBUFFERED=1

# Railway mapeará automáticamente el puerto 8080 al exterior
CMD uvicorn SOBERANO_03_NEXUS.index:app --host 0.0.0.0 --port 8080
