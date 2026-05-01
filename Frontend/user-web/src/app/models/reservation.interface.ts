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
  | 'CANCELADA'
  | 'EXPIRADA';

export interface ReservationOccupancy {
  adultos: number;
  ninos: number;
  infantes: number;
}

// ─── Category info from Catalog microservice ──────────────────────────────────
export interface CategoryInfo {
  id_categoria: string;
  nombre_comercial: string;
  foto_portada_url: string | null;
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
