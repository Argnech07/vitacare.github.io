# ============================================
# Dockerfile para Render.com
# ============================================

FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorio para uploads
RUN mkdir -p uploads/prescriptions

# Puerto por defecto (Render usa $PORT)
ENV PORT=8000

# Comando para iniciar
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
