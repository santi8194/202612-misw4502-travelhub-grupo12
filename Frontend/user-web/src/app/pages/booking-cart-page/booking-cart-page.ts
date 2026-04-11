import { Component, OnDestroy, computed, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { switchMap, catchError, of } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import { BookingStore } from '../../core/store/booking-store';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { BookingCartFormComponent } from '../../shared/components/booking-cart-page/form/booking-cart-form';
import { BookingCartSummaryComponent } from '../../shared/components/booking-cart-page/summary/booking-cart-summary';
import { BookingCartStepperComponent } from '../../shared/components/booking-cart-page/stepper/booking-cart-stepper';
import { GuestForm } from '../../models/guest.interface';
import { HoldRequest } from '../../models/hold.interface';
import { BookingSummaryData } from '../../models/booking-summary.interface';

interface BookingData {
  id_usuario?: string;
  id_categoria?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  fecha_check_in?: string;
  fecha_check_out?: string;
  num_huespedes?: number;
  ocupacion?: {
    adultos?: number;
    ninos?: number;
    infantes?: number;
  };
}

interface CatalogData {
  nombre?: string;
  propiedad_nombre?: string;
  ciudad?: string;
  pais?: string;
  imagen_principal_url?: string;
  precio_base?: string;
}

@Component({
  selector: 'app-booking-cart-page',
  imports: [
    HeaderComponent,
    FooterComponent,
    BookingCartStepperComponent,
    BookingCartFormComponent,
    BookingCartSummaryComponent,
  ],
  templateUrl: './booking-cart-page.html',
  styleUrl: './booking-cart-page.css'
})
export class BookingCartPage implements OnDestroy {
  private readonly bookingService = inject(BookingService);
  private readonly store = inject(BookingStore);
  private readonly route = inject(ActivatedRoute);

  form = signal<GuestForm>({
    name: '',
    lastName: '',
    email: '',
    phone: '',
    detailedRequest: ''
  });

  summary = signal<BookingSummaryData | null>(null);
  isLoadingSummary = signal(true);
  private bookingData = signal<BookingData | null>(null);

  remainingTime = signal(0);
  timerActive = computed(() => this.remainingTime() > 0);

  updateField(field: keyof GuestForm, value: string): void {
    this.form.update(current => ({ ...current, [field]: value }));
  }

  onFieldChange(event: { field: keyof GuestForm; value: string }): void {
    this.updateField(event.field, event.value);
  }

  private intervalId: ReturnType<typeof setInterval> | null = null;

  constructor() {
    this.loadHold();
    this.loadSummary();
  }

  private loadSummary(): void {
    const idReserva = this.route.snapshot.paramMap.get('id_reserva');
    console.info('[BookingCartPage] loadSummary start', { idReserva });

    if (!idReserva) {
      console.warn('[BookingCartPage] Missing id_reserva in route params');
      this.isLoadingSummary.set(false);
      return;
    }

    this.bookingService.getBookingById(idReserva).pipe(
      switchMap((booking: BookingData) => {
        console.info('[BookingCartPage] Booking loaded', booking);
        const categoryId = booking?.id_categoria;

        if (!categoryId) {
          console.warn('[BookingCartPage] Booking does not contain id_categoria', booking);
          return of({ booking, catalog: null });
        }

        return this.bookingService.getCatalogByCategoryId(categoryId).pipe(
          switchMap((catalog: CatalogData) => {
            console.info('[BookingCartPage] Catalog loaded', catalog);
            return of({ booking, catalog });
          }),
          catchError((error) => {
            console.error('[BookingCartPage] Catalog request failed', { categoryId, error });
            return of({ booking, catalog: null });
          })
        );
      }),
      catchError((error) => {
        console.error('[BookingCartPage] Booking request failed', { idReserva, error });
        return of(null);
      })
    ).subscribe((result) => {
      if (result?.booking) {
        const { booking, catalog } = result;
        this.bookingData.set(booking);

        const checkIn = this.extractCheckIn(booking);
        const checkOut = this.extractCheckOut(booking);
        const guests = this.extractGuests(booking);
        const nights = this.calcNights(checkIn, checkOut);
        const pricePerNight = Number.parseFloat(catalog?.precio_base ?? '0');
        const safePricePerNight = Number.isFinite(pricePerNight) ? pricePerNight : 0;
        const subtotal = safePricePerNight * nights;
        const serviceFee = Math.round(subtotal * 0.1);

        this.summary.set({
          propertyName: catalog?.propiedad_nombre ?? catalog?.nombre ?? 'N/A',
          location: catalog ? `${catalog.ciudad ?? 'N/A'}, ${catalog.pais ?? 'N/A'}` : 'N/A',
          imageUrl: catalog?.imagen_principal_url ?? '',
          checkIn,
          checkOut,
          guests,
          nights,
          pricePerNight: safePricePerNight,
          subtotal,
          serviceFee,
          total: subtotal + serviceFee,
        });
        console.info('[BookingCartPage] Summary computed', this.summary());
      } else {
        this.summary.set(null);
        console.warn('[BookingCartPage] Summary not available because booking was not loaded');
      }

      this.isLoadingSummary.set(false);
    });
  }

  private calcNights(from: string, to: string): number {
    if (!from || !to) {
      return 0;
    }

    const diff = new Date(to).getTime() - new Date(from).getTime();
    const nights = Math.round(diff / (1000 * 60 * 60 * 24));
    return nights > 0 ? nights : 0;
  }

  private extractCheckIn(booking: BookingData): string {
    return booking.fecha_inicio ?? booking.fecha_check_in ?? '';
  }

  private extractCheckOut(booking: BookingData): string {
    return booking.fecha_fin ?? booking.fecha_check_out ?? '';
  }

  private extractGuests(booking: BookingData): number {
    if (typeof booking.num_huespedes === 'number') {
      return booking.num_huespedes;
    }

    const ocupacion = booking.ocupacion;
    if (!ocupacion) {
      return 0;
    }

    return (ocupacion.adultos ?? 0) + (ocupacion.ninos ?? 0) + (ocupacion.infantes ?? 0);
  }

  createHold(): void {
    const booking = this.bookingData();
    if (!booking) {
      console.warn('[BookingCartPage] createHold blocked because booking data is missing');
      alert('No se pudo cargar la reserva desde backend');
      return;
    }

    const categoryId = booking.id_categoria;
    const checkIn = this.extractCheckIn(booking);
    const checkOut = this.extractCheckOut(booking);
    const guests = this.extractGuests(booking);

    if (!categoryId || !checkIn || !checkOut || guests <= 0) {
      console.error('[BookingCartPage] createHold blocked due to invalid backend booking data', {
        categoryId,
        checkIn,
        checkOut,
        guests,
        booking,
      });
      alert('La reserva no tiene todos los datos necesarios para crear el hold');
      return;
    }

    const request: HoldRequest = {
      categoryId,
      checkIn,
      checkOut,
      guests
    };
    console.info('[BookingCartPage] createHold request', request);

    this.bookingService.createHold(request).subscribe({
      next: (response) => {
        console.info('[BookingCartPage] createHold response', response);
        if (typeof response.expiresAt === 'number') {
          this.store.setHold(response);
          this.startTimer(response.expiresAt);
          return;
        }

        console.warn('[BookingCartPage] Hold response without expiresAt. Timer was not started.', response);
      },
      error: (error) => {
        console.error('[BookingCartPage] createHold failed', { request, error });
        this.clearTimer();
        this.remainingTime.set(0);
        this.store.clear();
        alert('No hay cupos disponibles');
      }
    });
  }

  private loadHold(): void {
    const hold = this.store.getHold();
    if (!hold) {
      return;
    }

    if (typeof hold.expiresAt !== 'number') {
      console.warn('[BookingCartPage] Stored hold has no expiresAt, clearing local hold', hold);
      this.store.clear();
      return;
    }

    const diff = Math.floor((hold.expiresAt - Date.now()) / 1000);
    if (diff <= 0) {
      this.store.clear();
      return;
    }

    this.startTimer(hold.expiresAt);
  }

  private startTimer(expiresAt: number): void {
    this.clearTimer();

    // Set immediately so the timer is visible before the first tick
    const initialDiff = Math.floor((expiresAt - Date.now()) / 1000);
    if (initialDiff <= 0) {
      this.store.clear();
      return;
    }
    this.remainingTime.set(initialDiff);

    this.intervalId = setInterval(() => {
      const diff = Math.floor((expiresAt - Date.now()) / 1000);

      if (diff <= 0) {
        this.clearTimer();
        this.remainingTime.set(0);
        this.store.clear();
        alert('El hold expiró');
      } else {
        this.remainingTime.set(diff);
      }
    }, 1000);
  }

  private clearTimer(): void {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  ngOnDestroy(): void {
    this.clearTimer();
  }
}
