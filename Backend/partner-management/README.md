# Partner Management Service

## Propósito

Servicio para aprobación o rechazo manual de reservas por parte de partners.

## Responsabilidad dentro del sistema

Valida que la reserva esté pendiente y publica el resultado de revisión manual para que `booking` continúe o compense la saga.

## Dependencias

- `booking`
- RabbitMQ
- Base de datos del servicio

## Requisitos

- Python
- Dependencias de `requirements.txt`

## Configuración

Variable relevante:

- `BOOKING_SERVICE_URL`

## Ejecución local

```bash
pip install -r requirements.txt
python main.py
```

## Pruebas

```bash
pytest
```

## Endpoints principales

- `GET /health`
- `POST /partner/reserva/{id_reserva}/aprobar`
- `POST /partner/reserva/{id_reserva}/rechazar`

## Eventos publicados y consumidos

- Publica `ReservaAprobadaManualEvt`.
- Publica `ReservaRechazadaManualEvt`.

## Persistencia

Gestiona información propia del dominio partner y apoya la validación de reservas pendientes.

## Documentación relacionada

- [`../../docs/microservicios/contratos-eventos.md`](../../docs/microservicios/contratos-eventos.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
