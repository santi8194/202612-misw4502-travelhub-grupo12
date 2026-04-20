# ── Etapa 1: builder ──────────────────────────────────────────────────────────
# Instala dependencias de producción en un directorio aislado para no
# contaminar la imagen final con herramientas de compilación.
FROM python:3.11-slim AS builder

WORKDIR /build

# Copiar solo el archivo de dependencias para aprovechar la caché de capas:
# si requirements.txt no cambia, Docker reutiliza esta capa en rebuilds.
COPY requirements.txt .

# Instalar en /install — se copiará a la imagen de runtime
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Etapa 2: runtime ──────────────────────────────────────────────────────────
# Imagen mínima de producción sin herramientas de build ni dependencias de test.
FROM python:3.11-slim AS runtime

# Crear grupo y usuario no-root para no ejecutar uvicorn con privilegios de root
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copiar las dependencias instaladas desde la etapa builder
COPY --from=builder /install /usr/local

# Copiar únicamente el código fuente de la aplicación
COPY app/ ./app/
COPY db/ ./db/
COPY entrypoint.sh ./entrypoint.sh

# Transferir la propiedad de los archivos al usuario no-root
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Iniciar uvicorn en modo producción (sin --reload)
ENTRYPOINT ["/app/entrypoint.sh"]
