from config.app import create_app
from modules.pms.infrastructure.services.consumer import start_consumer

import threading

app = create_app()

@app.on_event("startup")
def start_rabbitmq_consumer():

    thread = threading.Thread(target=start_consumer)
    thread.daemon = True
    thread.start()