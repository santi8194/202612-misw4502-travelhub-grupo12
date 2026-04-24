# Imagen base liviana
FROM python:3.11-slim

# Variables para evitar problemas de buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiamos requirements primero (cache eficiente)
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Exponemos puerto
EXPOSE 8001

# Comando para ejecutar el servicio
ENTRYPOINT ["/app/entrypoint.sh"]