# Notification Service

## Propósito

Servicio responsable de notificaciones de reserva por correo y push.

## Responsabilidad dentro del sistema

- Consume confirmaciones y cancelaciones de reserva.
- Persiste notificaciones de usuario.
- Publica el evento de voucher enviado.

## Dependencias

- RabbitMQ
- Base de datos del servicio
- Proveedor de correo
- Firebase Admin cuando se habilitan push notifications

## Requisitos

- Python
- Dependencias de `requirements.txt`

## Configuración

La configuración se define por variables de entorno, incluyendo conexión a RabbitMQ, base de datos y credenciales de correo.

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
- `GET /notificaciones`
- `PATCH /notificaciones/{id}/leida`
- `POST /notificaciones/device-token`
- `POST /notifications/reservations/status-email`

## Eventos publicados y consumidos

- Consume `ReservaConfirmadaEvt` y `ReservaCanceladaEvt`.
- Publica `VoucherEnviadoEvt`.

## Persistencia

Mantiene notificaciones y tokens de dispositivo.

## Documentación relacionada

- [`../../docs/microservicios/contratos-eventos.md`](../../docs/microservicios/contratos-eventos.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
