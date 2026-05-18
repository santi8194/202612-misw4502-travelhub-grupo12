# Booking Service

## Propósito

Servicio responsable de reservas y de la coordinación de la saga distribuida.

## Responsabilidad dentro del sistema

- Crear y consultar reservas.
- Orquestar pago, PMS, aprobación manual y voucher.
- Ejecutar compensaciones cuando un paso falla.

## Dependencias

- RabbitMQ
- Redis
- Base de datos del servicio
- `catalog`

## Requisitos

- Python
- Docker y Docker Compose para flujos integrados

## Configuración

La configuración de la saga se inicializa desde `config/seed.py`.

## Ejecución local

La ejecución integrada se documenta en [`ComoProbarSaga.md`](./ComoProbarSaga.md).

## Pruebas

```bash
pytest
```

## Endpoints principales

- `POST /reserva`
- `POST /reserva/{id_reserva}/formalizar`
- `GET /reserva/{id_reserva}`
- `GET /reserva/usuario/{id_usuario}`
- `POST /reserva/{id_reserva}/cancelar`

## Eventos publicados y consumidos

Participa en los eventos principales de la saga de reserva.

## Persistencia

Mantiene reservas, definiciones de saga, instancias y trazas de ejecución.

## Documentación relacionada

- [`./ComoProbarSaga.md`](./ComoProbarSaga.md)
- [`../../docs/arquitectura/flujos-criticos.md`](../../docs/arquitectura/flujos-criticos.md)
- [`../../docs/microservicios/contratos-eventos.md`](../../docs/microservicios/contratos-eventos.md)
