# ==============================================================================
# ARCHIVO: Dockerfile
# SISTEMA: MAESTRO-NEXUS
# PROPOSITO: Contenedor para ejecución persistente en Railway (Scheduler y Monitor)
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Variables de entorno por defecto (se sobrescriben en Railway)
ENV PYTHONUNBUFFERED=1

# Comando por defecto: ejecutar el scheduler (se puede sobrescribir en Railway)
CMD ["python3", "SOBERANO_02_CORE/core/scheduler.py"]
