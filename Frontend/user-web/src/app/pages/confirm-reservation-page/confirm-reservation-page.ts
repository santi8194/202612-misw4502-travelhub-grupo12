import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { BookingCartSummaryComponent } from '../../shared/components/booking-cart-page/summary/booking-cart-summary';
import { BookingCartStepperComponent } from '../../shared/components/booking-cart-page/stepper/booking-cart-stepper';
import { BookingService } from '../../core/services/booking';
import { CatalogService } from '../../core/services/catalog';
import { BookingSummaryData } from '../../models/booking-summary.interface';
import { RoomPriceResponse } from '../../models/room-price.interface';
import { catchError, forkJoin, of, switchMap } from 'rxjs';

interface BookingData {
  id_categoria?: string;
  estado?: string;
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
  precio_base?: {
    monto?: string | number;
    moneda?: string;
  };
}

interface PropertyData {
  nombre?: string;
  ubicacion?: {
    ciudad?: string;
    pais?: string;
  };
}

@Component({
  selector: 'app-confirm-reservation-page',
  standalone: true,
  imports: [
    RouterLink,
    HeaderComponent,
    FooterComponent,
    BookingCartStepperComponent,
    BookingCartSummaryComponent
  ],
  templateUrl: './confirm-reservation-page.html',
  styleUrl: './confirm-reservation-page.css',
})
export class ConfirmReservationPage {
  private static readonly DEFAULT_USER_COUNTRY = 'Colombia';

  private route = inject(ActivatedRoute);
  private bookingService = inject(BookingService);
  private catalogService = inject(CatalogService);

  summary = signal<BookingSummaryData | null>(null);
  isLoadingSummary = signal(true);
  bookingStatus = signal('');

  readonly reservationId = computed(
    () => this.route.snapshot.paramMap.get('id_reserva') ?? ''
  );

  readonly status = computed(
    () => (this.route.snapshot.queryParamMap.get('status') ?? 'rejected').trim().toLowerCase()
  );

  readonly isConfirmed = computed(
    () => this.status() === 'confirmed'
  );

  readonly isCancelled = computed(() => {
    const currentBookingStatus = this.normalizeText(this.bookingStatus());
    if (currentBookingStatus === 'cancelada' || currentBookingStatus === 'canceled' || currentBookingStatus === 'cancelled') {
      return true;
    }

    const currentStatus = this.status();
    if (currentStatus === 'cancelada' || currentStatus === 'canceled' || currentStatus === 'cancelled') {
      return true;
    }

    return this.normalizeText(this.reason()).includes('cancelad');
  });

  readonly reason = computed(
    () => this.route.snapshot.queryParamMap.get('reason') ??
      'No fue posible confirmar la reserva.'
  );

  constructor() {
    this.loadSummary();
  }

  private loadSummary() {
    const id = this.reservationId();

    if (!id) {
      this.isLoadingSummary.set(false);
      return;
    }

    this.bookingService.getBookingById(id).pipe(
      switchMap((booking: BookingData) => {
        const categoryId = booking?.id_categoria;

        if (!categoryId) {
          return of({ booking, catalog: null, category: null, property: null, roomPrice: null });
        }

        const checkIn = this.extractCheckIn(booking);
        const checkOut = this.extractCheckOut(booking);

        return forkJoin({
          catalog: this.bookingService.getCatalogByCategoryId(categoryId).pipe(
            catchError(() => of(null))
          ),
          category: this.bookingService.getCategoryById(categoryId).pipe(
            catchError(() => of(null))
          ),
          roomPrice: checkIn && checkOut
            ? this.catalogService.calculateRoomPrice({
              id_categoria: categoryId,
              fecha_inicio: checkIn,
              fecha_fin: checkOut,
              pais_usuario: ConfirmReservationPage.DEFAULT_USER_COUNTRY,
            }).pipe(
              catchError(() => of(null))
            )
            : of(null)
        }).pipe(
          switchMap(({ catalog, category, roomPrice }) => {
            const propertyId = category?.id_propiedad ?? catalog?.id_propiedad;
            if (!propertyId) {
              return of({ booking, catalog, category, property: null, roomPrice });
            }

            return this.bookingService.getPropertyById(propertyId).pipe(
              switchMap((property: PropertyData) => of({ booking, catalog, category, property, roomPrice })),
              catchError(() => of({ booking, catalog, category, property: null, roomPrice }))
            );
          })
        );
      }),
      catchError(() => of(null))
    ).subscribe((result) => {
      if (!result?.booking) {
        this.bookingStatus.set('');
        this.summary.set(null);
        this.isLoadingSummary.set(false);
        return;
      }

      const { booking, catalog, category, property, roomPrice } = result;
      this.bookingStatus.set(booking?.estado ?? '');
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
    const pricePerNight = Number.parseFloat(String(categoryAmount ?? catalog?.precio_base ?? '0'));
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

  private extractTaxesAndFees(roomPrice: RoomPriceResponse): number {
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

  private normalizeText(text: string): string {
    return text
      .trim()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  }

  showStatusNotAvailableAlert(): void {
    window.alert('Esta funcionalidad aun no esta disponible.');
  }
}