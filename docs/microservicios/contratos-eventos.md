# Contratos de eventos

## Convención general

- Exchange principal: `travelhub.events.exchange`
- Tipo de exchange: `topic`
- Convención recomendada de routing key: `evt.<dominio>.<resultado>`
- Excepción vigente: `pms.inventory.updated`

## Eventos principales

| Evento | Routing key | Publica | Consume | Propósito |
| --- | --- | --- | --- | --- |
| `ReservaCreadaIntegracionEvt` | `evt.reserva.creada` | `booking` | `booking`, `payment` | Iniciar flujo de reserva y pago |
| `PagoExitosoEvt` | `evt.pago.exitoso` | `payment` | `booking` | Continuar la saga tras pago aprobado |
| `PagoRechazadoEvt` | `evt.pago.rechazado` | `payment` | `booking` | Disparar compensación por rechazo de pago |
| `ConfirmacionPmsExitosaEvt` | `evt.pms.confirmacion_exitosa` | `pms-integration` | `booking` | Confirmar bloqueo o registro en PMS |
| `ReservaRechazadaPmsEvt` | `evt.pms.rechazada` | `pms-integration` | `booking` | Disparar compensación por rechazo PMS |
| `ReservaAprobadaManualEvt` | `evt.reserva.aprobada` | `partner-management` | `booking` | Continuar saga tras aprobación manual |
| `ReservaRechazadaManualEvt` | `evt.reserva.rechazada` | `partner-management` | `booking` | Disparar compensación por rechazo manual |
| `ReservaConfirmadaEvt` | `evt.reserva.confirmada` | `booking` | `notification` | Notificar confirmación al cliente |
| `ReservaCanceladaEvt` | `evt.reserva.cancelada` | `booking` | `notification` | Notificar cancelación al cliente |
| `VoucherEnviadoEvt` | `evt.voucher.enviado` | `notification` | `booking` | Cerrar flujo de voucher en la saga |
| `ConfirmacionPmsCanceladaEvt` | `evt.pms.reserva_cancelada` | `pms-integration` | `booking` | Confirmar cancelación en PMS |
| `PMSInventoryUpdated` | `pms.inventory.updated` | `pms-integration` | `catalog` | Actualizar inventario disponible |

## Observaciones

- `partner-management` publica eventos con envoltura CloudEvents 1.0.
- `notification` consume eventos de confirmación y cancelación y publica `VoucherEnviadoEvt`.
- La definición exacta de pasos de saga vive en `Backend/booking/config/seed.py`.
