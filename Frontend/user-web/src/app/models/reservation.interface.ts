// ─── Raw response from Booking microservice ───────────────────────────────────
export interface BookingReservation {
  id_reserva: string;
  id_usuario: string;
  id_categoria: string;
  estado: BookingEstado;
  fecha_check_in: string;
  fecha_check_out: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
  codigo_confirmacion_ota: string;
  codigo_localizador_pms: string;
  ocupacion: ReservationOccupancy;
}

export type BookingEstado =
  | 'HOLD'
  | 'PENDIENTE'
  | 'CONFIRMADA'
  | 'CANCELACION_EN_PROCESO'
  | 'CANCELADA'
  | 'EXPIRADA';

export interface ReservationOccupancy {
  adultos: number;
  ninos: number;
  infantes: number;
}

// ─── Payment info from Payment microservice ───────────────────────────────────
export type PaymentEstado =
  | 'PENDING'
  | 'APPROVED'
  | 'REJECTED'
  | 'CANCELLED'
  | 'REFUNDED';

export interface PaymentInfo {
  id_pago: string;
  id_reserva: string;
  estado: PaymentEstado;
  monto: number;
  moneda: string;
}

// ─── Catalog: GET /categories/{id_categoria} ──────────────────────────────────
export interface CategoryApiResponse {
  id_categoria: string;
  nombre_comercial: string;
  foto_portada_url: string | null;
}

// ─── Catalog: POST /calculate-room-price ──────────────────────────────────────
export interface CalculateRoomPriceResponse {
  total: number;
  moneda: string;
  noches: number;
  precio_por_noche: number;
  subtotal: number;
  impuestos: number;
  cargo_servicio: number;
}

// ─── Consolidated status for the view ─────────────────────────────────────────
// NOTE: resolved by reservation-status.resolver.ts
// When backend delivers unified status, only that file changes.
export type ReservationStatus =
  | 'PENDIENTE_PAGO'
  | 'PENDIENTE_CONFIRMACION_HOTEL'
  | 'CONFIRMADA'
  | 'CANCELADA';

// ─── View model consumed by the template ──────────────────────────────────────
export interface ReservationViewModel {
  id_reserva: string;
  nombre_comercial: string;
  foto_portada_url: string | null;
  estado: ReservationStatus;
  fecha_check_in: string;
  fecha_check_out: string;
  total_huespedes: number;
  monto_total: number | null;
  moneda: string;
  codigo_confirmacion: string | null;
}

// ─── Summary counters for the filter bar ──────────────────────────────────────
export interface ReservationCounters {
  total: number;
  confirmadas: number;
  pendientes: number;
  canceladas: number;
}

// ─── Active filter ─────────────────────────────────────────────────────────────
// PENDIENTE groups: PENDIENTE_PAGO + PENDIENTE_CONFIRMACION_HOTEL
export type ReservationFilter = 'TODAS' | 'CONFIRMADA' | 'PENDIENTE' | 'CANCELADA';

// ─── User locale (from public/assets/data/user-locale.json) ───────────────────
export interface UserLocale {
  pais: string;
  id_usuario: string;
}

// Cancellation flow contracts returned by Booking for HU-Web-11.
export type CancellationPolicyType =
  | 'FREE_CANCELLATION'
  | 'PARTIAL_REFUND'
  | 'NON_REFUNDABLE';

export type RefundStatus =
  | 'PENDING'
  | 'NOT_APPLICABLE';

export type PmsStatus =
  | 'PENDING'
  | 'CONFIRMED'
  | 'NOT_APPLICABLE';

export interface CancellationPolicy {
  type: CancellationPolicyType;
  label: string;
  description: string;
  diasAnticipacion: number;
  porcentajePenalidad: number;
}

export interface CancellationRefund {
  paidAmount: number;
  expectedRefundAmount: number;
  refundStatus: RefundStatus;
  processingTimeLabel: string;
}

export interface CancellationPreview {
  reservationId: string;
  reservationNumber: string;
  hotelName: string | null;
  location: string | null;
  checkInDate: string | null;
  checkOutDate: string | null;
  guests: number;
  currentStatus: BookingEstado;
  totalPaid: number;
  currency: string;
  canCancel: boolean;
  nonCancelableReason: string | null;
  pmsStatus: PmsStatus | null;
  mensaje: string | null;
  cancellationPolicy: CancellationPolicy;
  refund: CancellationRefund;
}

export interface CancelReservationRequest {
  acceptedTerms: boolean;
  reason?: string;
}

export interface CancellationResult {
  reservationId: string;
  reservationStatus: BookingEstado;
  cancellationReference: string;
  refundAmount: number;
  refundStatus: RefundStatus;
  processingTimeLabel: string | null;
  pmsStatus: PmsStatus;
  mensaje: string;
}
