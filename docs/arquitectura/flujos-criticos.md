# Flujos críticos

## Búsqueda de hospedaje

1. El frontend consulta `search` para destinos y resultados.
2. `search` resuelve consultas sobre PostgreSQL o OpenSearch según configuración.
3. `catalog` aporta información de propiedades, categorías e inventario cuando el flujo lo requiere.

## Reserva con saga

1. `booking` crea la reserva local.
2. La saga solicita procesamiento de pago.
3. `payment` publica resultado aprobado o rechazado.
4. `pms-integration` confirma o rechaza la reserva en PMS.
5. `partner-management` permite aprobación manual cuando el flujo la requiere.
6. `booking` confirma la reserva local.
7. `notification` consume el evento de confirmación y publica el envío de voucher.

Diagrama: [`diagramas/booking-saga.mmd`](./diagramas/booking-saga.mmd)

## Inventario PMS

1. `mock-pms` o un PMS externo reporta cambios.
2. `pms-integration` normaliza el payload.
3. Se publica `PMSInventoryUpdated`.
4. `catalog` consume el evento y actualiza inventario.

## Estados de reserva visibles al usuario

El frontend `user-web` combina información de `booking` y `payment` para resolver el estado visual mostrado al usuario. La regla vigente se documenta en [`../../Frontend/user-web/docs/regla_estados_cruzada.md`](../../Frontend/user-web/docs/regla_estados_cruzada.md).

## Lecturas relacionadas

- Eventos: [`../microservicios/contratos-eventos.md`](../microservicios/contratos-eventos.md)
- Prueba detallada de saga: [`../../Backend/booking/ComoProbarSaga.md`](../../Backend/booking/ComoProbarSaga.md)
