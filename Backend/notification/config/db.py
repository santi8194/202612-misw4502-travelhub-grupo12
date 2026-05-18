import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def _resolve_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    db_host = os.getenv("NOTIFICATION_DB_HOST") or os.getenv("DB_HOST")
    db_port = os.getenv("NOTIFICATION_DB_PORT") or os.getenv("DB_PORT") or "5432"
    db_name = os.getenv("NOTIFICATION_DB_NAME") or os.getenv("DB_NAME")
    db_user = os.getenv("NOTIFICATION_DB_USER") or os.getenv("DB_USER")
    db_password = os.getenv("NOTIFICATION_DB_PASSWORD") or os.getenv("DB_PASSWORD")

    if all([db_host, db_name, db_user, db_password]):
        return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    return "sqlite:///data/notification.db"


DATABASE_URL = _resolve_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
