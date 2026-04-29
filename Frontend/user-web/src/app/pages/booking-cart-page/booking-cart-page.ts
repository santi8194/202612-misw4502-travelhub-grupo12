import { Location } from '@angular/common';
import { Component, OnDestroy, computed, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Router } from '@angular/router';
import { switchMap, catchError, of, forkJoin, finalize } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import { PAYMENT_STORAGE_PREFIX } from '../../core/storage/payment-storage';
import { CatalogService } from '../../core/services/catalog';
import { BookingStore } from '../../core/store/booking-store';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { BookingCartFormComponent } from '../../shared/components/booking-cart-page/form/booking-cart-form';
import { BookingCartSummaryComponent } from '../../shared/components/booking-cart-page/summary/booking-cart-summary';
import { BookingCartStepperComponent } from '../../shared/components/booking-cart-page/stepper/booking-cart-stepper';
import { GuestForm } from '../../models/guest.interface';
import { HoldRequest } from '../../models/hold.interface';
import { BookingSummaryData } from '../../models/booking-summary.interface';
import { RoomPriceResponse } from '../../models/room-price.interface';

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
  id_propiedad?: string;
  nombre?: string;
  propiedad_nombre?: string;
  ciudad?: string;
  pais?: string;
  imagen_principal_url?: string;
  precio_base?: string;
}

interface CategoryData {
  id_propiedad?: string;
  nombre_comercial?: string;
  foto_portada_url?: string;
  monto_precio_base?: string | number;
  moneda_precio_base?: string;
  precio_base?: {
    monto?: string | number;
    moneda?: string;
  };
}

interface PropertyData {
  id_propiedad?: string;
  nombre?: string;
  ubicacion?: {
    ciudad?: string;
    pais?: string;
  };
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
  private static readonly HOLD_DURATION_MS = 15 * 60 * 1000;
  private static readonly OPTIMISTIC_HOLD_ID = 'optimistic-hold';
  private static readonly DEFAULT_USER_COUNTRY = 'Colombia';

  private readonly bookingService = inject(BookingService);
  private readonly catalogService = inject(CatalogService);
  private readonly store = inject(BookingStore);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly location = inject(Location);
  private hasSentExpireRequest = false;
  private readonly reservationId = this.route.snapshot.paramMap.get('id_reserva');

  form = signal<GuestForm>({
    name: '',
    lastName: '',
    email: '',
    phone: '',
    detailedRequest: ''
  });

  summary = signal<BookingSummaryData | null>(null);
  isLoadingSummary = signal(true);
  isSubmittingPayment = signal(false);
  isRedirectingToExistingSession = signal(false);
  holdError = signal<string | null>(null);
  private bookingData = signal<BookingData | null>(null);
  private propertyIdForBack = signal<string | null>(null);

  remainingTime = signal(0);
  timerActive = computed(() => this.remainingTime() > 0);
  isHoldExpiringSoon = computed(() => this.remainingTime() > 0 && this.remainingTime() <= 120);
  formattedRemainingTime = computed(() => {
    const total = Math.max(this.remainingTime(), 0);
    const minutes = Math.floor(total / 60).toString().padStart(2, '0');
    const seconds = (total % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  });

  isGuestFormComplete = computed(() => {
    const currentForm = this.form();
    const name = currentForm.name.trim();
    const lastName = currentForm.lastName.trim();
    const email = currentForm.email.trim();
    const phone = currentForm.phone.trim();
    const emailIsValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    return name.length > 0 && lastName.length > 0 && phone.length > 0 && emailIsValid;
  });

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
          return of({ booking, catalog: null, category: null, property: null, roomPrice: null });
        }

        const checkIn = this.extractCheckIn(booking);
        const checkOut = this.extractCheckOut(booking);

        return forkJoin({
          catalog: this.bookingService.getCatalogByCategoryId(categoryId).pipe(
            catchError((error) => {
              console.error('[BookingCartPage] Catalog request failed', { categoryId, error });
              return of(null);
            })
          ),
          category: this.bookingService.getCategoryById(categoryId).pipe(
            catchError((error) => {
              console.error('[BookingCartPage] Category request failed', { categoryId, error });
              return of(null);
            })
          ),
          roomPrice: checkIn && checkOut
            ? this.catalogService.calculateRoomPrice({
              id_categoria: categoryId,
              fecha_inicio: checkIn,
              fecha_fin: checkOut,
              pais_usuario: BookingCartPage.DEFAULT_USER_COUNTRY,
            }).pipe(
              catchError((error) => {
                console.error('[BookingCartPage] Room price request failed', { categoryId, checkIn, checkOut, error });
                return of(null);
              })
            )
            : of(null)

        }).pipe(
          switchMap(({ catalog, category, roomPrice }) => {
            console.info('[BookingCartPage] Catalog loaded', catalog);
            console.info('[BookingCartPage] Category loaded', category);
            console.info('[BookingCartPage] Room price loaded', roomPrice);
            return of({ booking, catalog, category, roomPrice });
          })
        ).pipe(
          switchMap(({ booking, catalog, category, roomPrice }) => {
            const propertyId = category?.id_propiedad ?? catalog?.id_propiedad;
            if (!propertyId) {
              console.warn('[BookingCartPage] Property id not found in category/catalog payloads');
              return of({ booking, catalog, category, property: null, roomPrice });
            }

            return this.bookingService.getPropertyById(propertyId).pipe(
              switchMap((property: PropertyData) => {
                console.info('[BookingCartPage] Property loaded', property);
                return of({ booking, catalog, category, property, roomPrice });
              }),
              catchError((error) => {
                console.error('[BookingCartPage] Property request failed', { propertyId, error });
                return of({ booking, catalog, category, property: null, roomPrice });
              })
            );
          })
        );
      }),
      catchError((error) => {
        console.error('[BookingCartPage] Booking request failed', { idReserva, error });
        return of(null);
      })
    ).subscribe((result) => {
      if (result?.booking) {
        const { booking, catalog, category, property, roomPrice } = result;
        this.bookingData.set(booking);
        this.propertyIdForBack.set(property?.id_propiedad ?? category?.id_propiedad ?? catalog?.id_propiedad ?? null);

        if (this.redirectToExistingSessionIfNeeded(booking)) {
          this.isLoadingSummary.set(false);
          return;
        }

        this.syncCurrentSession();

        const checkIn = this.extractCheckIn(booking);
        const checkOut = this.extractCheckOut(booking);
        const guests = this.extractGuests(booking);
        const nights = this.calcNights(checkIn, checkOut);

        const pricing = this.resolveSummaryPricing(roomPrice, category, catalog, nights);
        const categoryName = category?.nombre_comercial;
        const propertyName = property?.nombre ?? catalog?.propiedad_nombre ?? catalog?.nombre ?? 'N/A';
        const city = property?.ubicacion?.ciudad ?? catalog?.ciudad ?? 'N/A';
        const country = property?.ubicacion?.pais ?? catalog?.pais ?? 'N/A';

        this.summary.set({
          propertyName: categoryName
            ? `${propertyName} - ${categoryName}`
            : propertyName,
          location: `${city}, ${country}`,
          imageUrl: category?.foto_portada_url ?? catalog?.imagen_principal_url ?? '',
          checkIn,
          checkOut,
          guests,
          nights: pricing.nights,
          pricePerNight: pricing.pricePerNight,
          subtotal: pricing.subtotal,
          taxesAndFees: pricing.taxesAndFees,
          total: pricing.total,
          currency: pricing.currency,
          currencySymbol: pricing.currencySymbol,
          taxesAndFeesLabel: pricing.taxesAndFeesLabel,
        });
        console.info('[BookingCartPage] Summary computed', this.summary());
      } else {
        this.summary.set(null);
        console.warn('[BookingCartPage] Summary not available because booking was not loaded');
      }

      this.isLoadingSummary.set(false);
    });
  }

  goBack(): void {
    if (window.history.length > 1) {
      this.location.back();
      return;
    }

    const propertyId = this.propertyIdForBack();
    const booking = this.bookingData();
    const categoryId = booking?.id_categoria ?? '';
    const checkIn = booking ? this.extractCheckIn(booking) : '';
    const checkOut = booking ? this.extractCheckOut(booking) : '';
    const guests = booking ? this.extractGuests(booking) : 1;

    if (categoryId) {
      this.router.navigate(['/category', categoryId], {
        queryParams: {
          fecha_inicio: checkIn,
          fecha_fin: checkOut,
          huespedes: guests,
        },
      });
      return;
    }

    if (propertyId) {
      this.router.navigate(['/property', propertyId], {
        queryParams: {
          id_categoria: booking?.id_categoria ?? '',
          fecha_inicio: checkIn,
          fecha_fin: checkOut,
          huespedes: guests,
        },
      });
      return;
    }

    console.warn('[BookingCartPage] Property id unavailable for back navigation, redirecting to resultados');
    this.router.navigate(['/resultados']);
  }

  private calcNights(from: string, to: string): number {
    if (!from || !to) {
      return 0;
    }

    const diff = new Date(to).getTime() - new Date(from).getTime();
    const nights = Math.round(diff / (1000 * 60 * 60 * 24));
    return nights > 0 ? nights : 0;
  }

  private resolveSummaryPricing(
    roomPrice: RoomPriceResponse | null,
    category: CategoryData | null,
    catalog: CatalogData | null,
    nights: number,
  ) {
    if (roomPrice) {
      const taxesAndFees = this.extractTaxesAndFees(roomPrice);
      return {
        nights: roomPrice.noches > 0 ? roomPrice.noches : nights,
        pricePerNight: roomPrice.precio_por_noche ?? 0,
        subtotal: roomPrice.subtotal ?? 0,
        taxesAndFees,
        total: roomPrice.total ?? (roomPrice.subtotal ?? 0) + taxesAndFees,
        currency: roomPrice.moneda ?? 'COP',
        currencySymbol: roomPrice.simbolo_moneda ?? '$',
        taxesAndFeesLabel: roomPrice.impuesto_nombre ? `${roomPrice.impuesto_nombre} y cargos` : 'Impuestos y cargos',
      };
    }

    const categoryAmount = category?.precio_base?.monto ?? category?.monto_precio_base;
    const fallbackCategoryAmount = category?.precio_base;
    const pricePerNight = Number.parseFloat(
      String(categoryAmount ?? fallbackCategoryAmount ?? catalog?.precio_base ?? '0')
    );
    const safePricePerNight = Number.isFinite(pricePerNight) ? pricePerNight : 0;
    const subtotal = safePricePerNight * nights;
    const taxesAndFees = Math.round(subtotal * 0.1);

    return {
      nights,
      pricePerNight: safePricePerNight,
      subtotal,
      taxesAndFees,
      total: subtotal + taxesAndFees,
      currency: 'COP',
      currencySymbol: '$',
      taxesAndFeesLabel: 'Impuestos y cargos',
    };
  }

  private extractTaxesAndFees(roomPrice: RoomPriceResponse & { impuestos_y_cargos?: number }): number {
    if (typeof roomPrice.impuestos_y_cargos === 'number') {
      return roomPrice.impuestos_y_cargos;
    }

    return (roomPrice.impuestos ?? 0) + (roomPrice.cargo_servicio ?? 0);
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
    if (!this.isGuestFormComplete()) {
      this.holdError.set('Completa la información del huésped principal (nombre, apellido, email válido y celular) para continuar.');
      return;
    }

    if (!this.timerActive()) {
      this.holdError.set('El tiempo de hold expiró. Debes volver a seleccionar la reserva.');
      console.warn('[BookingCartPage] createHold blocked because optimistic hold has expired');
      alert('El tiempo de hold expiró. Debes volver a seleccionar la reserva.');
      return;
    }

    if (this.isSubmittingPayment()) {
      return;
    }

    if (!this.reservationId) {
      this.holdError.set('No se encontró el identificador de la reserva. Regresa y crea una nueva reserva.');
      console.warn('[BookingCartPage] createHold blocked because reservation id is missing');
      return;
    }

    const booking = this.bookingData();
    if (!booking) {
      this.holdError.set('No se pudo cargar la reserva desde backend. Vuelve a intentarlo más tarde.');
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
      this.holdError.set('La reserva no tiene todos los datos necesarios para continuar con el pago.');
      alert('La reserva no tiene todos los datos necesarios para crear el hold');
      return;
    }

    const request: HoldRequest = {
      categoryId,
      checkIn,
      checkOut,
      guests,
    };

    const currentSession = this.getCurrentBookingSession();
    if (currentSession && currentSession.expiresAt > Date.now()) {
      console.info('[BookingCartPage] Reusing active booking session', currentSession);
      this.startTimer(currentSession.expiresAt);
    }

    this.holdError.set(null);
    console.info('[BookingCartPage] createHold request', request);

    const hold = this.store.getHold(this.reservationId);
    const expiresAt = hold?.expiresAt && hold.expiresAt > Date.now()
      ? hold.expiresAt
      : Date.now() + BookingCartPage.HOLD_DURATION_MS;

    this.store.setHold(this.reservationId, { id: this.reservationId ?? BookingCartPage.OPTIMISTIC_HOLD_ID, expiresAt });
    this.storeCurrentSession(expiresAt);
    this.startTimer(expiresAt);

    console.info('[BookingCartPage] Formalizing reservation from continue payment button', {
      reservationId: this.reservationId,
      timerActive: this.timerActive(),
    });

    const total = Number(this.summary()?.total);
    if (!Number.isFinite(total) || total <= 0) {
      this.holdError.set('No fue posible calcular el valor total de la reserva para iniciar el pago.');
      return;
    }

    this.isSubmittingPayment.set(true);
    this.bookingService.formalizeBookingById(this.reservationId, {
      intencion_pago: {
        monto: total,
        moneda: 'COP',
      },
    }).pipe(
      finalize(() => this.isSubmittingPayment.set(false))
    ).subscribe({
      next: (response) => {
        const reason = response?.mensaje?.trim() || 'Tu reserva está siendo procesada por la saga.';
        if (response.pago?.checkout) {
          sessionStorage.setItem(
            `${PAYMENT_STORAGE_PREFIX}${this.reservationId}`,
            JSON.stringify(response.pago)
          );
          this.router.navigate(['/booking', this.reservationId, 'payment']);
          return;
        }

        this.holdError.set('La reserva fue formalizada, pero el backend no devolvió una intención de pago para Wompi. Intenta nuevamente o valida el payload de formalización.');
        console.error('[BookingCartPage] formalizeBookingById response without Wompi checkout', {
          reservationId: this.reservationId,
          response,
          reason,
        });
      },
      error: (error) => {
        const reason = this.bookingService.getReservationErrorMessage(
          error,
          'No fue posible formalizar la reserva. Intenta nuevamente.'
        );
        this.holdError.set(reason);
        this.router.navigate(['/booking', this.reservationId, 'confirm-reservation'], {
          queryParams: {
            status: 'rejected',
            reason,
          },
        });
      }
    });
  }

  private loadHold(): void {
    const hold = this.store.getHold(this.reservationId);
    if (!hold) {
      this.initializeOptimisticHold();
      return;
    }

    if (typeof hold.expiresAt !== 'number') {
      console.warn('[BookingCartPage] Stored hold has no expiresAt, clearing local hold', hold);
      this.store.clear(this.reservationId);
      this.clearCurrentSession();
      this.initializeOptimisticHold();
      return;
    }

    const diff = Math.floor((hold.expiresAt - Date.now()) / 1000);
    if (diff <= 0) {
      this.store.clear(this.reservationId);
      this.clearCurrentSession();
      this.initializeOptimisticHold();
      return;
    }

    this.startTimer(hold.expiresAt);
  }

  private initializeOptimisticHold(): void {
    const expiresAt = Date.now() + BookingCartPage.HOLD_DURATION_MS;
    this.store.setHold(this.reservationId, { id: BookingCartPage.OPTIMISTIC_HOLD_ID, expiresAt });
    this.storeCurrentSession(expiresAt);
    this.startTimer(expiresAt);
    console.info('[BookingCartPage] Optimistic hold initialized', { reservationId: this.reservationId, expiresAt });
  }

  private startTimer(expiresAt: number): void {
    this.clearTimer();

    // Set immediately so the timer is visible before the first tick
    const initialDiff = Math.floor((expiresAt - Date.now()) / 1000);
    if (initialDiff <= 0) {
      this.store.clear(this.reservationId);
      this.clearCurrentSession();
      return;
    }
    this.remainingTime.set(initialDiff);

    this.intervalId = setInterval(() => {
      const diff = Math.floor((expiresAt - Date.now()) / 1000);

      if (diff <= 0) {
        this.clearTimer();
        this.remainingTime.set(0);
        this.store.clear(this.reservationId);
        this.clearCurrentSession();
        this.expireReservationIfNeeded();
      } else {
        this.remainingTime.set(diff);
      }
    }, 1000);
  }

  private expireReservationIfNeeded(): void {
    if (this.hasSentExpireRequest) {
      return;
    }

    const idReserva = this.route.snapshot.paramMap.get('id_reserva');
    if (!idReserva) {
      console.warn('[BookingCartPage] Cannot expire reservation: missing id_reserva in route');
      return;
    }

    this.hasSentExpireRequest = true;
    this.bookingService.expireBookingById(idReserva).subscribe({
      next: (response) => {
        console.info('[BookingCartPage] Reservation expired in backend', { idReserva, response });
      },
      error: (error) => {
        console.error('[BookingCartPage] Failed to expire reservation in backend', { idReserva, error });
      }
    });
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

  private buildBookingSignature(booking: BookingData): string | null {
    const categoryId = booking.id_categoria ?? '';
    const checkIn = this.extractCheckIn(booking);
    const checkOut = this.extractCheckOut(booking);
    const guests = this.extractGuests(booking);

    if (!categoryId || !checkIn || !checkOut || guests <= 0) {
      return null;
    }

    return [categoryId, checkIn, checkOut, guests].join('|');
  }

  private getCurrentBookingSession() {
    const booking = this.bookingData();
    const signature = booking ? this.buildBookingSignature(booking) : null;
    return signature ? this.store.getBookingSession(signature) : null;
  }

  private storeCurrentSession(expiresAt: number): void {
    const booking = this.bookingData();
    const signature = booking ? this.buildBookingSignature(booking) : null;
    if (!signature || !this.reservationId) {
      return;
    }

    this.store.setBookingSession(signature, {
      reservationId: this.reservationId,
      signature,
      expiresAt,
    });
  }

  private clearCurrentSession(): void {
    const booking = this.bookingData();
    const signature = booking ? this.buildBookingSignature(booking) : null;
    if (!signature) {
      return;
    }

    const session = this.store.getBookingSession(signature);
    if (session?.reservationId === this.reservationId) {
      this.store.clearBookingSession(signature);
    }
  }

  private syncCurrentSession(): void {
    const hold = this.store.getHold(this.reservationId);
    if (hold?.expiresAt && hold.expiresAt > Date.now()) {
      this.storeCurrentSession(hold.expiresAt);
    }
  }

  private redirectToExistingSessionIfNeeded(booking: BookingData): boolean {
    const signature = this.buildBookingSignature(booking);
    if (!signature) {
      return false;
    }

    const existingSession = this.store.getBookingSession(signature);
    if (!existingSession || existingSession.reservationId === this.reservationId || existingSession.expiresAt <= Date.now()) {
      if (existingSession && existingSession.expiresAt <= Date.now()) {
        this.store.clearBookingSession(signature);
      }
      return false;
    }

    this.holdError.set('Ya existe una reserva activa con la misma información. Te redirigimos a esa sesión.');
    this.isRedirectingToExistingSession.set(true);
    this.clearTimer();
    this.remainingTime.set(0);
    console.info('[BookingCartPage] Redirecting to existing booking session', existingSession);
    this.router.navigate(['/booking', existingSession.reservationId]);
    return true;
  }
}
