import importlib


DB_ENV_VARS = (
    'PAYMENT_DB_USER',
    'PAYMENT_DB_PASSWORD',
    'PAYMENT_DB_HOST',
    'PAYMENT_DB_PORT',
    'PAYMENT_DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'DB_HOST',
    'DB_PORT',
    'DB_NAME',
)


def _reload_database(monkeypatch):
    for key in DB_ENV_VARS:
        monkeypatch.delenv(key, raising=False)

    import modules.payments.infrastructure.database as database

    return importlib.reload(database)


def test_payment_uses_sqlite_when_db_env_is_missing(monkeypatch):
    database = _reload_database(monkeypatch)

    assert database.IS_SQLITE is True
    assert database.DATABASE_URL.endswith('/data/payments.db')
    assert database.engine.url.drivername == 'sqlite'


def test_payment_uses_payment_prefixed_postgres_env(monkeypatch):
    database = _reload_database(monkeypatch)
    monkeypatch.setenv('PAYMENT_DB_USER', 'payment_user')
    monkeypatch.setenv('PAYMENT_DB_PASSWORD', 'payment_password')
    monkeypatch.setenv('PAYMENT_DB_HOST', 'payment-db')
    monkeypatch.setenv('PAYMENT_DB_PORT', '5433')
    monkeypatch.setenv('PAYMENT_DB_NAME', 'payment_db')

    assert (
        database.build_database_url()
        == 'postgresql+psycopg2://payment_user:payment_password@payment-db:5433/payment_db'
    )


def test_payment_accepts_shared_db_env_fallback(monkeypatch):
    database = _reload_database(monkeypatch)
    monkeypatch.setenv('DB_USER', 'shared_user')
    monkeypatch.setenv('DB_PASSWORD', 'shared_password')
    monkeypatch.setenv('DB_HOST', 'shared-db')
    monkeypatch.setenv('DB_NAME', 'shared_payment_db')

    assert (
        database.build_database_url()
        == 'postgresql+psycopg2://shared_user:shared_password@shared-db:5432/shared_payment_db'
    )
