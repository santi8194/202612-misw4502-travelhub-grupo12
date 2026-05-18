# Catalog Service

## Propósito

Servicio de catálogo para propiedades, categorías, precios, temporadas e inventario.

## Responsabilidad dentro del sistema

Proveer información comercial y disponibilidad consumida por búsqueda, reserva y frontends.

## Dependencias

- Base de datos del servicio
- RabbitMQ para inventario PMS

## Requisitos

- Python
- Dependencias de `requirements.txt`

## Configuración

Soporta ejecución local y procesamiento opcional de eventos.

## Ejecución local

Consultar:

- [`QUICK_START.md`](./QUICK_START.md)
- [`DOCKER.md`](./DOCKER.md)

## Pruebas

```bash
pytest
```

## Endpoints principales

- `GET /catalog/health`
- `POST /catalog/properties`
- `GET /catalog/properties`
- `GET /catalog/categories/{id_categoria}`
- `PUT /catalog/properties/{id_propiedad}/categories/{id_categoria}/inventory`

## Eventos publicados y consumidos

- Consume `PMSInventoryUpdated`.

## Persistencia

Gestiona propiedades, categorías, precios, temporadas e inventario.

## Documentación relacionada

- [`./scripts/README_SEED.md`](./scripts/README_SEED.md)
- [`./SEED_SUMMARY_100.md`](./SEED_SUMMARY_100.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
