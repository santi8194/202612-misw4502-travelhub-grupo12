from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

def _env(*keys):
	for key in keys:
		value = os.getenv(key)
		if value:
			return value
	return None

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, '..', '..', '..', 'data')
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, 'payments.db')

db_user = _env('PAYMENT_DB_USER', 'DB_USER')
db_password = _env('PAYMENT_DB_PASSWORD', 'DB_PASSWORD')
db_host = _env('PAYMENT_DB_HOST', 'DB_HOST')
db_port = _env('PAYMENT_DB_PORT', 'DB_PORT') or '5432'
db_name = _env('PAYMENT_DB_NAME', 'DB_NAME')

if all([db_user, db_password, db_host, db_name]):
	DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
else:
	DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()