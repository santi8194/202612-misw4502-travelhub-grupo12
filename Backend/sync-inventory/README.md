# SyncInventory

Microservicio FastAPI que simula integraciones con varios PMS, transforma datos externos al contrato interno del agregado `Inventario` y los envia desacoplados por HTTP al `InventoryService`.

## Estructura

```text
Backend/sync-inventory
|-- app.py
|-- requirements.txt
|-- README.md
|-- src
|   |-- bootstrap.py
|   |-- config.py
|   |-- controllers
|   |   |-- health_controller.py
|   |   |-- schemas.py
|   |   `-- sync_controller.py
|   |-- application
|   |   |-- sync_service.py
|   |   `-- transformation_service.py
|   |-- domain
|   |   |-- enums.py
|   |   |-- models.py
|   |   `-- ports.py
|   `-- infrastructure
|       |-- logging.py
|       |-- adapters
|       |   `-- mock_pms_adapter.py
|       |-- clients
|       |   `-- inventory_service_client.py
|       |-- idempotency
|       |   `-- in_memory_store.py
|       |-- queue
|       |   `-- in_memory_retry_queue.py
|       `-- scheduling
|           `-- sync_scheduler.py
`-- tests
    |-- test_smoke.py
    `-- test_sync_service.py
```

## Como correrlo

```bash
cd Backend/sync-inventory
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8010
```

Variables opcionales:

```bash
set INVENTORY_SERVICE_BASE_URL=http://localhost:8000
set POLLING_ENABLED=true
set EVENT_SIMULATION_ENABLED=true
set PROPERTY_POLL_INTERVAL_SECONDS=20
set ROOM_TYPE_POLL_INTERVAL_SECONDS=30
set AVAILABILITY_POLL_INTERVAL_SECONDS=15
set RATE_POLL_INTERVAL_SECONDS=25
set EVENT_SIMULATION_INTERVAL_SECONDS=12
```

## Ejemplo de ejecucion

1. Arranca `SyncInventory`.
2. El scheduler hace polling periodico a los adapters mock de PMS.
3. En paralelo, el simulador genera cambios webhook-like.
4. Cada cambio se transforma y se envia a `InventoryService`.
5. Si llega el mismo evento o payload otra vez, la capa de idempotencia lo salta.
6. Si el `InventoryService` falla, el comando se pone en una cola en memoria para reintento.

Tambien puedes disparar sincronizaciones manuales:

```bash
curl -X POST http://localhost:8010/sync/properties
curl -X POST http://localhost:8010/sync/room-types
curl -X POST http://localhost:8010/sync/availability
curl -X POST http://localhost:8010/sync/rates
curl -X POST http://localhost:8010/simulation/events/property
curl http://localhost:8010/sync/status
```

Webhook-like manual:

```bash
curl -X POST http://localhost:8010/webhooks/pms/property ^
  -H "Content-Type: application/json" ^
  -d "{\"event_id\":\"pms-event-1001\",\"source_system\":\"demo-pms\",\"records\":[{\"property_id\":\"f47ac10b-58cc-4372-a567-0e02b2c3d479\",\"nombre\":\"Hotel Boutique Las Palmas\",\"estrellas\":4,\"ubicacion\":{\"ciudad\":\"Cartagena\",\"pais\":\"Colombia\",\"coordenadas\":{\"lat\":10.42,\"lng\":-75.54}},\"porcentaje_impuesto\":19.0,\"updated_at\":\"2026-03-29T12:00:00Z\"}]}"
```

## Payload de ejemplo enviado a InventoryService

Endpoint destino:

```text
POST /inventory/sync/property
```

Body:

```json
{
  "eventId": "mock-pms-property-000001",
  "idempotencyKey": "d384f38d0a2d0c7992dadb8d4ca6880207463fe06b6e91fb471a2a12fd6c29c0",
  "resourceType": "property",
  "sourceSystem": "mock-pms",
  "trigger": "polling",
  "occurredAt": "2026-03-29T17:00:00+00:00",
  "payload": {
    "idPropiedad": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "nombre": "Hotel Boutique Las Palmas",
    "estrellas": 4,
    "ubicacion": {
      "ciudad": "Cartagena",
      "pais": "Colombia",
      "coordenadas": {
        "lat": 10.42,
        "lng": -75.54
      }
    },
    "porcentajeImpuesto": 19.0
  }
}
```

## Notas de arquitectura

- No hay persistencia propia del dominio.
- No se implementa logica de inventario.
- La responsabilidad del servicio es integracion, transformacion y orquestacion.
- El desacople con `InventoryService` se hace via HTTP client.
- La idempotencia usa `event_id` y hash canonico del payload transformado.
- Los mocks de `Propiedad`, `Categoria_Habitacion`, `Amenidad`, `Media` e `Inventario` quedaron alineados con la documentacion compartida.
