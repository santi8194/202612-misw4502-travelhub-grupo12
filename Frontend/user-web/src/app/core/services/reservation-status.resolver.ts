import {
  BookingEstado,
  PaymentEstado,
  ReservationStatus,
} from '../../models/reservation.interface';

/**
 * Resolves the unified view status from Booking + Payment states.
 *
 * ─── ISOLATION STRATEGY ───────────────────────────────────────────────────────
 * This is the ONLY place where cross-service state logic lives.
 * When the backend delivers a unified status, replace this function body
 * with a direct mapping — zero changes to service, page, or card components.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export function resolveReservationStatus(
  bookingEstado: BookingEstado,
  paymentEstado: PaymentEstado | null
): ReservationStatus {
  if (bookingEstado === 'CONFIRMADA') return 'CONFIRMADA';
  if (bookingEstado === 'CANCELADA') return 'CANCELADA';

  // HOLD state: cross with payment to determine sub-state
  if (bookingEstado === 'HOLD' || bookingEstado === 'PENDIENTE') {
    if (paymentEstado === 'APPROVED') return 'PENDIENTE_CONFIRMACION_HOTEL';
    return 'PENDIENTE_PAGO';
  }

  // EXPIRADA or unknown: treat as cancelled for display
  return 'CANCELADA';
}

/** Maps a ReservationStatus to a human-readable Spanish label */
export function getStatusLabel(status: ReservationStatus): string {
  const labels: Record<ReservationStatus, string> = {
    PENDIENTE_PAGO: 'Pendiente Pago',
    PENDIENTE_CONFIRMACION_HOTEL: 'Pendiente Confirmación',
    CONFIRMADA: 'Confirmada',
    CANCELADA: 'Cancelada',
  };
  return labels[status];
}
