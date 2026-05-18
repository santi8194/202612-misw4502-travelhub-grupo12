# Search Service

## Propósito

Servicio de búsqueda de hospedajes y autocompletado de destinos.

## Responsabilidad dentro del sistema

Resolver consultas de búsqueda desacopladas del catálogo transaccional.

## Dependencias

- PostgreSQL por defecto
- OpenSearch opcional

## Requisitos

- Python
- Dependencias de `requirements.txt`

## Configuración

Variable relevante:

- `REPOSITORY_TYPE`

## Ejecución local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Pruebas

```bash
pytest
```

## Endpoints principales

- `GET /health`
- `GET /api/v1/search`
- `GET /api/v1/search/destinations`

## Eventos publicados y consumidos

No participa en la mensajería principal de la saga.

## Persistencia

Consulta datos de hospedajes y destinos en el motor configurado.

## Documentación relacionada

- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
- [`../../docs/arquitectura/flujos-criticos.md`](../../docs/arquitectura/flujos-criticos.md)
