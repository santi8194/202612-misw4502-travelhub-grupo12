import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { toSignal } from '@angular/core/rxjs-interop';
import { forkJoin, Observable, of, switchMap } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import {
  BookingReservation,
  CalculateRoomPriceResponse,
  CategoryApiResponse,
  PaymentEstado,
  PaymentInfo,
  ReservationCounters,
  ReservationFilter,
  ReservationViewModel,
  UserLocale,
} from '../../models/reservation.interface';
import { resolveReservationStatus, getStatusLabel } from './reservation-status.resolver';

@Injectable({ providedIn: 'root' })
export class MyReservationsService {
  private readonly http = inject(HttpClient);
  private readonly bookingApiUrl = environment.bookingApiUrl;
  private readonly catalogApiUrl = environment.catalogApiUrl;
  private readonly paymentApiUrl = environment.paymentApiUrl;

  readonly reservations = toSignal(this.loadReservations$(), { initialValue: [] });

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

  readonly getStatusLabel = getStatusLabel;

  private loadReservations$(): Observable<ReservationViewModel[]> {
    return this.http.get<UserLocale>('assets/data/user-locale.json').pipe(
      switchMap(locale =>
        this.http.get<BookingReservation[]>(
          `${this.bookingApiUrl}/usuario/${locale.id_usuario}`
        ).pipe(
          switchMap(bookings =>
            bookings.length === 0
              ? of([])
              : forkJoin(
                  bookings.map(booking =>
                    this.enrichReservation$(booking, locale.pais)
                  )
                )
          )
        )
      ),
      catchError(() => of([]))
    );
  }

  private enrichReservation$(
    booking: BookingReservation,
    pais: string
  ): Observable<ReservationViewModel> {
    return forkJoin({
      category: this.http.get<CategoryApiResponse>(
        `${this.catalogApiUrl}/categories/${booking.id_categoria}`
      ).pipe(catchError(() => of(null))),
      payments: this.http.get<PaymentInfo[]>(
        `${this.paymentApiUrl}/payments/by-reserva/${booking.id_reserva}`
      ).pipe(catchError(() => of([]))),
    }).pipe(
      switchMap(({ category, payments }) => {
        const approvedPayment = payments.find(p => p.state === 'APPROVED') ?? null;

        if (approvedPayment) {
          return of(
            this.buildViewModel(
              booking, category,
              approvedPayment.amount, approvedPayment.currency,
              'APPROVED'
            )
          );
        }

        const firstPaymentState: PaymentEstado | null = payments[0]?.state ?? null;

        return this.http.post<CalculateRoomPriceResponse>(
          `${this.catalogApiUrl}/calculate-room-price`,
          {
            id_categoria: booking.id_categoria,
            fecha_inicio: booking.fecha_check_in,
            fecha_fin: booking.fecha_check_out,
            pais_usuario: pais,
          }
        ).pipe(
          catchError(() => of(null)),
          map(priceCalc =>
            this.buildViewModel(
              booking, category,
              priceCalc?.total ?? null,
              priceCalc?.moneda ?? '',
              firstPaymentState
            )
          )
        );
      })
    );
  }

  private buildViewModel(
    booking: BookingReservation,
    category: CategoryApiResponse | null,
    monto_total: number | null,
    moneda: string,
    paymentStateForResolver: PaymentEstado | null
  ): ReservationViewModel {
    const estado = resolveReservationStatus(booking.estado, paymentStateForResolver);

    return {
      id_reserva: booking.id_reserva,
      nombre_comercial: category?.nombre_comercial ?? '—',
      foto_portada_url: category?.foto_portada_url ?? null,
      estado,
      fecha_check_in: booking.fecha_check_in,
      fecha_check_out: booking.fecha_check_out,
      total_huespedes:
        (booking.ocupacion?.adultos ?? 0) +
        (booking.ocupacion?.ninos ?? 0) +
        (booking.ocupacion?.infantes ?? 0),
      monto_total,
      moneda,
      codigo_confirmacion:
        booking.codigo_confirmacion_ota || booking.codigo_localizador_pms || null,
    };
  }
}
