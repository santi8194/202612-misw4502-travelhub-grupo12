FROM python:3.10-slim

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código al contenedor
COPY . .

# Script de entrada que ejecuta migraciones y luego inicia FastAPI
RUN echo '#!/bin/bash\n\
echo "Waiting for database to be ready..."\n\
sleep 10\n\
echo "Running database migrations..."\n\
python -m alembic upgrade head\n\
if [ $? -ne 0 ]; then\n\
  echo "Migration failed!"\n\
  exit 1\n\
fi\n\
echo "Starting FastAPI server..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /src/entrypoint.sh && chmod +x /src/entrypoint.sh

# Comando para ejecutar FastAPI con migraciones
ENTRYPOINT ["/src/entrypoint.sh"]
