
FROM python:3.11-slim

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r requirements.txt
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
