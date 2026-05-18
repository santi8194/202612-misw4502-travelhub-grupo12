# Auth Service

## Propósito

Servicio de autenticación para registro, inicio de sesión y emisión de tokens JWT.

## Responsabilidad dentro del sistema

Centraliza autenticación y consulta de identidad para el resto de componentes.

## Dependencias

- Base de datos del servicio

## Requisitos

- Python
- Dependencias de `requirements.txt`

## Configuración

Se configura por variables de entorno propias del servicio.

## Ejecución local

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Pruebas

```bash
python -m pytest --maxfail=1 --disable-warnings --cov=. --cov-report=term-missing --cov-fail-under=80
```

## Endpoints principales

- `POST /login`
- `POST /register`
- `POST /register/confirm`
- `GET /me`
- `POST /refresh`

## Eventos publicados y consumidos

No participa en la mensajería principal de la saga.

## Persistencia

Gestiona usuarios y datos asociados a autenticación.

## Documentación relacionada

- [`../../docs/api/autenticacion.md`](../../docs/api/autenticacion.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
