FROM python:3.10-slim

WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN sed -i 's/\r$//' /src/entrypoint.sh && chmod +x /src/entrypoint.sh

ENTRYPOINT ["/src/entrypoint.sh"]
