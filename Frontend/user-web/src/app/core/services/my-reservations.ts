import { Injectable, computed, signal } from '@angular/core';
import {
  ReservationCounters,
  ReservationFilter,
  ReservationViewModel,
} from '../../models/reservation.interface';
import { resolveReservationStatus, getStatusLabel } from './reservation-status.resolver';

/** ─── PHASE 1: MOCK DATA ──────────────────────────────────────────────────────
 * In Phase 2, replace MOCK_RESERVATIONS with toSignal(httpObservable$)
 * that fetches from Booking → Catalog → Payment and maps to ReservationViewModel.
 */
const MOCK_RESERVATIONS: ReservationViewModel[] = [
  {
    id_reserva: '441619ae-308c-46bb-ad23-971ced60f3e1',
    nombre_comercial: 'Bourdeaux Getaway',
    foto_portada_url: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80',
    estado: resolveReservationStatus('CONFIRMADA', 'APPROVED'),
    fecha_check_in: '2026-03-07',
    fecha_check_out: '2026-03-10',
    total_huespedes: 2,
    monto_total: 580,
    moneda: 'USD',
    codigo_confirmacion: 'TH-GP-001-2026',
  },
  {
    id_reserva: 'b2e34f77-1234-4abc-9def-56789abcdef0',
    nombre_comercial: 'Coastal Bay Resort',
    foto_portada_url: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80',
    estado: resolveReservationStatus('HOLD', null),
    fecha_check_in: '2026-04-09',
    fecha_check_out: '2026-04-14',
    total_huespedes: 4,
    monto_total: 1725,
    moneda: 'USD',
    codigo_confirmacion: null,
  },
  {
    id_reserva: 'c3d45e88-5678-4bcd-aef0-67890bcdef01',
    nombre_comercial: 'Mountain View Lodge',
    foto_portada_url: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    estado: resolveReservationStatus('CANCELADA', null),
    fecha_check_in: '2026-02-09',
    fecha_check_out: '2026-02-12',
    total_huespedes: 2,
    monto_total: 1275,
    moneda: 'USD',
    codigo_confirmacion: null,
  },
];

@Injectable({ providedIn: 'root' })
export class MyReservationsService {
  /** Phase 1: static signal. Phase 2: replace with toSignal(http$) */
  readonly reservations = signal<ReservationViewModel[]>(MOCK_RESERVATIONS);

  readonly activeFilter = signal<ReservationFilter>('TODAS');

  readonly filteredReservations = computed(() => {
    const filter = this.activeFilter();
    const all = this.reservations();

    if (filter === 'TODAS') return all;
    if (filter === 'PENDIENTE') {
      return all.filter(
        r =>
          r.estado === 'PENDIENTE_PAGO' ||
          r.estado === 'PENDIENTE_CONFIRMACION_HOTEL'
      );
    }
    return all.filter(r => r.estado === filter);
  });

  readonly counters = computed<ReservationCounters>(() => {
    const all = this.reservations();
    return {
      total: all.length,
      confirmadas: all.filter(r => r.estado === 'CONFIRMADA').length,
      pendientes: all.filter(
        r =>
          r.estado === 'PENDIENTE_PAGO' ||
          r.estado === 'PENDIENTE_CONFIRMACION_HOTEL'
      ).length,
      canceladas: all.filter(r => r.estado === 'CANCELADA').length,
    };
  });

  setFilter(filter: ReservationFilter): void {
    this.activeFilter.set(filter);
  }

  /** Exposed for template use */
  readonly getStatusLabel = getStatusLabel;
}
