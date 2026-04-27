import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def _build_database_url() -> str:
	db_host = os.getenv("DB_HOST")
	db_port = os.getenv("DB_PORT", "5432")
	db_name = os.getenv("DB_NAME")
	db_user = os.getenv("DB_USER")
	db_password = os.getenv("DB_PASSWORD")

	if db_host and db_name and db_user and db_password:
		return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

	# SQLite local path (override with SQLITE_DIR). In Docker local this should
	# resolve to /app/data to persist through the mounted volume.
	data_dir = os.getenv("SQLITE_DIR")
	if not data_dir:
		if os.path.isdir("/app/data"):
			data_dir = "/app/data"
		else:
			current_dir = os.path.dirname(os.path.abspath(__file__))
			data_dir = os.path.join(current_dir, "..", "..", "..", "data")
	os.makedirs(data_dir, exist_ok=True)
	db_path = os.path.join(data_dir, "catalog.db")
	return f"sqlite:///{db_path}"


DATABASE_URL = _build_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
	connect_args={"check_same_thread": False} if IS_SQLITE else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()