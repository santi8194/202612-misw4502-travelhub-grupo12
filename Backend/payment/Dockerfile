# Imagen base liviana
FROM python:3.11-slim

# Variables para evitar problemas de buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY models.py .
COPY wompi_client.py .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt


# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
# Copiamos el resto del proyecto
COPY . .
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Exponemos puerto
EXPOSE 8002

# Comando para ejecutar el servicio
ENTRYPOINT ["/app/entrypoint.sh"]
