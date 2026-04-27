import threading

from app import app
from modules.payments.infrastructure.services.consumer import start_consumer    

@app.on_event("startup")
def start_rabbitmq_consumer():

    thread = threading.Thread(target=start_consumer)
    thread.daemon = True
    thread.start()
