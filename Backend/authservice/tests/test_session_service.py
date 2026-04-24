"""
Tests para session_service.
Tras la migración a Cognito, el módulo es un placeholder de auditoría.
Se valida que el módulo se importa sin errores.
"""


def test_session_service_module_imports():
    import modules.session_service  # noqa: F401
    assert True