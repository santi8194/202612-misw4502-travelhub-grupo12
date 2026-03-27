from app import SERVICE_NAME, healthcheck


def test_service_name_matches_directory() -> None:
    assert SERVICE_NAME == "pms-integration"


def test_healthcheck_returns_ok() -> None:
    assert healthcheck() == "ok"
