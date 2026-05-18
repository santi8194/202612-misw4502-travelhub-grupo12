# Payment Service

## Propósito

Servicio responsable de pagos, tarjetas, checkout y recepción de webhooks de Wompi.

## Responsabilidad dentro del sistema

Procesar pagos asociados a reservas y publicar el resultado hacia la saga.

## Dependencias

- Wompi
- RabbitMQ
- Base de datos del servicio

## Requisitos

- Python
- Variables sandbox de Wompi para pruebas locales

## Configuración

Variables relevantes:

- `WOMPI_PUBLIC_KEY`
- `WOMPI_PRIVATE_KEY`
- `WOMPI_INTEGRITY_SECRET`
- `WOMPI_EVENTS_SECRET`
- `WOMPI_BASE_URL`
- `WOMPI_PAYOUTS_BASE_URL`

## Ejecución local

```powershell
.\scripts\start-local.ps1
```

## Pruebas

```bash
pytest
```

## Endpoints principales

- `GET /health`
- `POST /payments`
- `GET /payments/by-reserva/{id_reserva}`
- `POST /payments/cards/tokenize`
- `POST /webhook`

## Eventos publicados y consumidos

- Consume `evt.reserva.creada`.
- Publica `PagoExitosoEvt` y `PagoRechazadoEvt`.

## Persistencia

Mantiene pagos y estado de transacciones.

## Documentación relacionada

- [`../../docs/microservicios/contratos-eventos.md`](../../docs/microservicios/contratos-eventos.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
