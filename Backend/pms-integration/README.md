# PMS Integration Service

## Propósito

Servicio de integración entre TravelHub y proveedores PMS.

## Responsabilidad dentro del sistema

Confirmar o cancelar reservas en PMS y normalizar cambios de inventario externos.

## Dependencias

- PMS externo o `mock-pms`
- RabbitMQ
- Base de datos del servicio

## Requisitos

- Python
- Dependencias de `requirements.txt`

## Configuración

Permite seleccionar adaptador PMS mediante encabezado `X-PMS-Provider` en webhooks de inventario.

## Ejecución local

```bash
docker build -t pmsintegration .
docker run -p 8001:8001 -v $(pwd)/data:/app/data pmsintegration
```

## Pruebas

```bash
pytest
```

## Endpoints principales

- `GET /health`
- `POST /confirmar-reserva`
- `POST /cancelar-reserva`
- `POST /webhooks/inventory`

## Eventos publicados y consumidos

- Publica `ConfirmacionPmsExitosaEvt`.
- Publica `ReservaRechazadaPmsEvt`.
- Publica `ConfirmacionPmsCanceladaEvt`.
- Publica `PMSInventoryUpdated`.

## Persistencia

Mantiene información de reservas sincronizadas con PMS.

## Documentación relacionada

- [`../../docs/microservicios/contratos-eventos.md`](../../docs/microservicios/contratos-eventos.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
