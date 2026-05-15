
import os

class Settings:
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS: str = os.getenv("RABBITMQ_PASS", "guest")
    
    MOCK_PMS_URL: str = os.getenv("MOCK_PMS_URL", "http://mock-pms:8080")
    POLLING_INTERVAL_SECONDS: int = int(os.getenv("POLLING_INTERVAL_SECONDS", 120))
    ENABLE_POLLING: bool = os.getenv("ENABLE_POLLING", "true").lower() == "true"

settings = Settings()