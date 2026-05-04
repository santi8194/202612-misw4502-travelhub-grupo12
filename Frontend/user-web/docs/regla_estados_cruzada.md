# Regla de Estados Cruzada (Booking × Payment)

Este documento describe la lógica de orquestación en el FrontEnd (`user-web`) para determinar el estado visual de una reserva basado en la información de los microservicios de **Booking** y **Payment**.

## 1. Lógica de Resolución de Estados

Dado que el backend actualmente no entrega un estado único consolidado, el FrontEnd aplica la siguiente matriz de decisión (implementada en `reservation-status.resolver.ts`):

| Estado Booking | Respuesta Payment | Estado Visual (View Model) | Color Badge |
| :--- | :--- | :--- | :--- |
| `HOLD` | `404 Not Found` / `PENDING` | **Pendiente Pago** | Naranja (`#ff6900`) |
| `HOLD` | `APPROVED` | **Pendiente Confirmación Hotel** | Amarillo (`#f59e0b`) |
| `CONFIRMADA` | (No importa) | **Confirmada** | Verde (`#00c950`) |
| `CANCELADA` | (No importa) | **Cancelada** | Gris (`#364153`) |
| `EXPIRADA` | (No importa) | **Cancelada** | Gris (`#364153`) |

## 2. Endpoints Involucrados en la Orquestación

Para construir la vista de "Mis Reservas", el servicio `MyReservationsService` realiza las siguientes llamadas:

1.  **Booking Service**: `GET /booking/api/reserva/usuario/{id_usuario}`
    *   Obtiene la lista base de reservas del usuario.
    *   Provee: `id_reserva`, `id_categoria`, `estado` (Booking).

2.  **Catalog Service**: `GET /catalog/categories/{id_categoria}`
    *   Se llama por cada reserva para obtener detalles estéticos.
    *   Provee: `nombre_comercial`, `foto_portada_url`.

3.  **Payment Service**: `GET /payment/payments/by-reserva/{id_reserva}`
    *   Se llama por cada reserva para verificar el flujo de caja.
    *   Provee: `estado` (Payment). Si retorna `404`, se asume que no hay pago iniciado.

## 3. Relación con los Filtros de UI

Los estados visuales se agrupan en los filtros superiores de la pantalla de la siguiente manera:

*   **TODAS**: Muestra todo el universo de reservas.
*   **CONFIRMADA**: Reservas en estado `CONFIRMADA`.
*   **PENDIENTE**: Grupo que une `PENDIENTE_PAGO` y `PENDIENTE_CONFIRMACION_HOTEL`.
*   **CANCELADA**: Reservas en estado `CANCELADA`.

## 4. Estrategia de Aislamiento

Toda esta lógica reside exclusivamente en `reservation-status.resolver.ts`. 

> [!IMPORTANT]
> Si en el futuro el Backend unifica estos estados en un solo campo, **solo se debe modificar el resolver**, manteniendo intactos los componentes de la interfaz (`MyReservationsPage`, `ReservationCard`).
