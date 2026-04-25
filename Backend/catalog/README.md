# Catalog Service

Microservicio de catalogo para TravelHub con una estructura ligera inspirada en arquitectura hexagonal.

## Estructura

- `config/`: inicializacion y acceso a SQLite.
- `data/`: base de datos local `catalog.db`.
- `modules/catalog/`: dominio, puertos, servicio de aplicacion, adaptador SQLite y API HTTP.
- `tests/`: pruebas de smoke y flujo principal.
- `app.py` y `main.py`: bootstrap de FastAPI.

## Dominio

El servicio modela:

- `Propiedad` como raiz de agregado.
- `Categoria_Habitacion` para contenido OTA.
- `Media`, `Amenidad` e `Inventario`.
- Objetos de valor para direccion, dinero y politica de cancelacion.

## Endpoints principales

- `GET /catalog/health`
- `POST /catalog/properties`
- `GET /catalog/properties`
- `GET /catalog/properties/{property_id}`
- `PUT /catalog/properties/{property_id}/categories/{category_id}/inventory`
- `GET /catalog/properties/{property_id}/categories/{category_id}/availability/{inventory_date}`

## Ejecucion local

```bash
pip install -r requirements.txt
uvicorn main:app --reload
pytest
pytest --cov=api --cov=config --cov=main --cov=modules/catalog --cov-report=term-missing
```

## PostgreSQL / RDS

Cuando `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD` estan
definidas, el servicio usa PostgreSQL. En ese modo el schema debe quedar
administrado por Alembic; `main.py` solo ejecuta `create_all()` para el flujo
historico con SQLite local.
