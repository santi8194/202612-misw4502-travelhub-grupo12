FROM python:3.12-slim

WORKDIR /src/Booking
COPY . /src/Booking

ENV PYTHONPATH=/src
ENV FLASK_APP=api

RUN pip install --no-cache-dir -r requirements.txt
RUN sed -i 's/\r$//' /src/Booking/entrypoint.sh && chmod +x /src/Booking/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/src/Booking/entrypoint.sh"]
