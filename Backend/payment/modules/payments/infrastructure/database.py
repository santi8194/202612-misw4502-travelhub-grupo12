import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def _env(*keys):
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def _sqlite_database_path() -> Path:
    current_dir = Path(__file__).resolve().parent
    data_dir = current_dir / '..' / '..' / '..' / 'data'
    data_dir = data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / 'payments.db'


def build_database_url() -> str:
    db_user = _env('PAYMENT_DB_USER', 'DB_USER')
    db_password = _env('PAYMENT_DB_PASSWORD', 'DB_PASSWORD')
    db_host = _env('PAYMENT_DB_HOST', 'DB_HOST')
    db_port = _env('PAYMENT_DB_PORT', 'DB_PORT') or '5432'
    db_name = _env('PAYMENT_DB_NAME', 'DB_NAME')

    if all([db_user, db_password, db_host, db_name]):
        return f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    return f"sqlite:///{_sqlite_database_path().as_posix()}"


DATABASE_URL = build_database_url()
IS_SQLITE = DATABASE_URL.startswith('sqlite')

connect_args = {'check_same_thread': False} if IS_SQLITE else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
