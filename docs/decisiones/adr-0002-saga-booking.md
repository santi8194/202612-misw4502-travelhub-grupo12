# ADR-0002: Saga orquestada para reservas

## Estado

Aceptado

## Contexto

La reserva involucra pago, PMS, aprobación manual y notificación, con posibilidad de fallos parciales.

## Decisión

Usar una saga orquestada desde `booking`, con pasos configurados, eventos de resultado y compensaciones LIFO.

## Consecuencias

- Permite consistencia eventual y recuperación explícita.
- Requiere eventos idempotentes y trazabilidad del flujo.
- Hace necesario documentar el contrato de eventos.
