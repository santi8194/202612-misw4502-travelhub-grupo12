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

const DUMMY_SUMMARY: BookingSummaryData = {
  propertyName: 'Bourdeaux Getaway',
  location: 'Bourdeaux, Francia',
  imageUrl: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2',
  checkIn: 'Mar 07, 2026',
  checkOut: 'Mar 10, 2026',
  guests: 2,
  nights: 3,
  pricePerNight: 175,
  subtotal: 525,
  serviceFee: 55,
  total: 580,
};

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

  summary = signal<BookingSummaryData>(DUMMY_SUMMARY);
  isLoadingSummary = signal(true);

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
    if (!idReserva) {
      this.isLoadingSummary.set(false);
      return;
    }

    this.bookingService.getBookingById(idReserva).pipe(
      switchMap((booking) =>
        this.bookingService.getCatalogByCategoryId(booking.id_categoria).pipe(
          catchError(() => of(null)),
          switchMap((catalog) => of({ booking, catalog }))
        )
      ),
      catchError(() => of(null))
    ).subscribe((result) => {
      if (result?.booking) {
        const { booking, catalog } = result;
        const nights = this.calcNights(booking.fecha_inicio, booking.fecha_fin);
        const pricePerNight = catalog?.precio_base ? parseFloat(catalog.precio_base) : DUMMY_SUMMARY.pricePerNight;
        const subtotal = pricePerNight * nights;
        const serviceFee = Math.round(subtotal * 0.1);
        this.summary.set({
          propertyName: catalog?.propiedad_nombre ?? catalog?.nombre ?? DUMMY_SUMMARY.propertyName,
          location: catalog ? `${catalog.ciudad}, ${catalog.pais}` : DUMMY_SUMMARY.location,
          imageUrl: catalog?.imagen_principal_url ?? DUMMY_SUMMARY.imageUrl,
          checkIn: booking.fecha_inicio ?? DUMMY_SUMMARY.checkIn,
          checkOut: booking.fecha_fin ?? DUMMY_SUMMARY.checkOut,
          guests: booking.num_huespedes ?? DUMMY_SUMMARY.guests,
          nights,
          pricePerNight,
          subtotal,
          serviceFee,
          total: subtotal + serviceFee,
        });
      }
      this.isLoadingSummary.set(false);
    });
  }

  private calcNights(from: string, to: string): number {
    const diff = new Date(to).getTime() - new Date(from).getTime();
    const nights = Math.round(diff / (1000 * 60 * 60 * 24));
    return nights > 0 ? nights : DUMMY_SUMMARY.nights;
  }

  private static readonly OPTIMISTIC_HOLD_MS = 10 * 60 * 1000; // 10 min fallback

  createHold(): void {
    const request: HoldRequest = {
      categoryId: 1,
      checkIn: '2026-10-10',
      checkOut: '2026-10-15',
      guests: 2
    };

    // Optimistic: show timer immediately with an estimated expiry
    const optimisticExpiresAt = Date.now() + BookingCartPage.OPTIMISTIC_HOLD_MS;
    this.store.setHold({ id: 'optimistic', expiresAt: optimisticExpiresAt });
    this.startTimer(optimisticExpiresAt);

    this.bookingService.createHold(request).subscribe({
      next: (response) => {
        // Reconcile with real server expiry
        this.store.setHold(response);
        this.startTimer(response.expiresAt);
      },
      error: () => {
        // Roll back optimistic hold
        this.clearTimer();
        this.remainingTime.set(0);
        this.store.clear();
        alert('No hay cupos disponibles');
      }
    });
  }

  private loadHold(): void {
    const hold = this.store.getHold();
    if (!hold) return;

    const diff = Math.floor((hold.expiresAt - Date.now()) / 1000);
    if (diff <= 0) {
      // Expired while the user was away
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
