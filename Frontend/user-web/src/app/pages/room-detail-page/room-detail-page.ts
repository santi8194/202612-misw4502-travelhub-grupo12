import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, finalize, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { BookingService } from '../../core/services/booking';
import { CatalogService } from '../../core/services/catalog';
import { BookingStore } from '../../core/store/booking-store';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HeaderComponent } from '../../shared/components/header/header';
import { RoomDetailResponse } from '../../models/room-detail.interface';
import { RoomPriceResponse } from '../../models/room-price.interface';

@Component({
  selector: 'app-room-detail-page',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './room-detail-page.html',
  styleUrl: './room-detail-page.css',
})
export class RoomDetailPage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly http = inject(HttpClient);
  private readonly catalogService = inject(CatalogService);
  private readonly bookingService = inject(BookingService);
  private readonly store = inject(BookingStore);

  // ── Estado ──
  readonly loading = signal(true);
  readonly creatingBooking = signal(false);
  readonly error = signal<string | null>(null);
  readonly roomDetail = signal<RoomDetailResponse | null>(null);
  readonly descriptionExpanded = signal(false);

  // ── Precio calculado ──
  readonly roomPrice = signal<RoomPriceResponse | null>(null);
  readonly loadingPrice = signal(false);
  readonly paisUsuario = signal('Colombia');

  // ── Datos de búsqueda (solo lectura — vienen de query params) ──
  readonly checkInInput = signal('');
  readonly checkOutInput = signal('');
  readonly guestsInput = signal(1);

  // ── Computados ──
  readonly categoryId = computed(() => this.route.snapshot.paramMap.get('category_id') ?? '');
  readonly todayIso = computed(() => new Date().toISOString().split('T')[0]);

  readonly nightsCount = computed(() => {
    const checkIn = this.checkInInput();
    const checkOut = this.checkOutInput();
    if (!checkIn || !checkOut) return 0;
    const diff = new Date(checkOut).getTime() - new Date(checkIn).getTime();
    const nights = Math.round(diff / (1000 * 60 * 60 * 24));
    return nights > 0 ? nights : 0;
  });

  readonly pricePerNight = computed(() => {
    const fromApi = this.roomPrice()?.precio_por_noche;
    if (fromApi != null) return fromApi;
    const monto = this.roomDetail()?.categoria?.precio_base?.monto;
    const parsed = Number(monto ?? '0');
    return Number.isFinite(parsed) ? parsed : 0;
  });

  readonly subtotal = computed(() => this.roomPrice()?.subtotal ?? 0);
  readonly total = computed(() => this.roomPrice()?.total ?? 0);

  readonly impuestos = computed(() => this.roomPrice()?.impuestos ?? 0);
  readonly cargoServicio = computed(() => this.roomPrice()?.cargo_servicio ?? 0);
  readonly impuestoNombre = computed(() => this.roomPrice()?.impuesto_nombre ?? 'IVA');

  readonly currencySymbol = computed(() => {
    const fromApi = this.roomPrice()?.simbolo_moneda;
    if (fromApi) return fromApi;
    const moneda = this.roomDetail()?.categoria?.precio_base?.moneda ?? 'COP';
    return moneda === 'USD' ? '$' : moneda;
  });

  readonly canReserve = computed(() => {
    const checkIn = this.checkInInput();
    const checkOut = this.checkOutInput();
    return !!checkIn && !!checkOut && checkOut > checkIn && this.guestsInput() > 0;
  });

  readonly galleryImages = computed(() => {
    const galeria = this.roomDetail()?.galeria ?? [];
    const sorted = [...galeria].sort((a, b) => a.orden - b.orden);
    // Fill up to 5 slots with the available images (repeat last if needed)
    const slots = 5;
    if (sorted.length === 0) return Array(slots).fill('');
    return Array.from({ length: slots }, (_, i) => sorted[Math.min(i, sorted.length - 1)].url_full);
  });

  readonly shortDescription = computed(() => {
    const desc = this.roomDetail()?.categoria?.descripcion ?? '';
    return desc.length > 240 ? desc.slice(0, 240) + '...' : desc;
  });

  readonly amenityIconSvg: Record<string, string> = {
    'pool-icon': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20M7 12V7a5 5 0 0 1 10 0v5"/><path d="M2 17c1.5 1.5 3.5 1.5 5 0s3.5-1.5 5 0 3.5 1.5 5 0"/></svg>`,
    'spa-icon': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c4-4 8-8 8-12a8 8 0 0 0-16 0c0 4 4 8 8 12z"/></svg>`,
    'kitchen-icon': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h.01M15 9h.01M9 15h.01M15 15h.01M12 12h.01"/></svg>`,
    'gym-icon': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16M18 4v16M4 9h2M18 9h2M4 15h2M18 15h2M8 9h8M8 15h8"/></svg>`,
    'restaurant-icon': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2l1 10h16L21 2M12 12v10M8 22h8"/></svg>`,
    'ac-icon': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="8" rx="2"/><path d="M6 14v2M12 14v4M18 14v2M9 20h6"/></svg>`,
    'default': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>`,
  };

  getAmenityIcon(icono: string): string {
    return this.amenityIconSvg[icono] ?? this.amenityIconSvg['default'];
  }

  formatDate(isoDate: string): string {
    if (!isoDate) return '';
    const date = new Date(isoDate);
    return date.toLocaleDateString('es-CO', { year: 'numeric', month: 'long' });
  }

  formatCurrency(amount: number): string {
    if (!amount) return '0';
    return amount.toLocaleString('es-CO');
  }

  constructor() {
    this.checkInInput.set(this.route.snapshot.queryParamMap.get('fecha_inicio') ?? '');
    this.checkOutInput.set(this.route.snapshot.queryParamMap.get('fecha_fin') ?? '');
    this.guestsInput.set(Number(this.route.snapshot.queryParamMap.get('huespedes') ?? '1') || 1);
    this.http.get<{ pais: string }>('/assets/data/user-locale.json').subscribe({
      next: (data) => this.paisUsuario.set(data.pais),
      error: () => console.warn('[RoomDetailPage] Could not load user-locale.json, using default'),
    });
    this.loadRoomDetail();
  }

  private loadRoomDetail(): void {
    const categoryId = this.categoryId();
    if (!categoryId) {
      this.error.set('No se encontró el identificador de la categoría.');
      this.loading.set(false);
      console.warn('[RoomDetailPage] Missing category_id route param');
      return;
    }

    console.info('[RoomDetailPage] Loading room detail', { categoryId });

    this.catalogService.getCategoryViewDetail(categoryId).pipe(
      catchError((err) => {
        console.error('[RoomDetailPage] getCategoryViewDetail failed', { categoryId, err });
        this.error.set('No fue posible cargar el detalle de la habitación.');
        return of(null);
      }),
      finalize(() => this.loading.set(false))
    ).subscribe(response => {
      if (response) {
        this.roomDetail.set(response);
        console.info('[RoomDetailPage] Room detail loaded', response);
        this.calculatePrice();
      }
    });
  }

  private calculatePrice(): void {
    const categoryId = this.categoryId();
    const checkIn = this.checkInInput();
    const checkOut = this.checkOutInput();
    if (!categoryId || !checkIn || !checkOut || checkOut <= checkIn) return;

    this.loadingPrice.set(true);
    this.catalogService.calculateRoomPrice({
      id_categoria: categoryId,
      fecha_inicio: checkIn,
      fecha_fin: checkOut,
      pais_usuario: this.paisUsuario(),
    }).pipe(
      finalize(() => this.loadingPrice.set(false))
    ).subscribe({
      next: (price) => {
        this.roomPrice.set(price);
        console.info('[RoomDetailPage] Room price calculated', price);
      },
      error: (err) => console.error('[RoomDetailPage] calculateRoomPrice failed', err),
    });
  }

  toggleDescription(): void {
    this.descriptionExpanded.update(v => !v);
  }

  reservar(): void {
    const categoryId = this.categoryId();
    const checkIn = this.checkInInput();
    const checkOut = this.checkOutInput();
    const guests = this.guestsInput();

    if (!categoryId || !checkIn || !checkOut || checkOut <= checkIn || guests <= 0) {
      console.error('[RoomDetailPage] reservar blocked due to missing or invalid data', {
        categoryId, checkIn, checkOut, guests,
      });
      this.error.set('Faltan datos para crear la reserva. Verifica las fechas e inténtalo de nuevo.');
      return;
    }

    const signature = this.buildSessionSignature(categoryId, checkIn, checkOut, guests);
    const activeSession = this.store.getBookingSession(signature);
    if (activeSession) {
      if (activeSession.expiresAt > Date.now()) {
        this.router.navigate(['/existing-session-redirect'], {
          queryParams: {
            reservationId: activeSession.reservationId,
          },
        });
        return;
      }

      this.store.clearBookingSession(signature);
    }

    this.creatingBooking.set(true);
    this.error.set(null);

    const request = {
      id_usuario: this.resolveUserId(),
      id_categoria: categoryId,
      fecha_check_in: checkIn,
      fecha_check_out: checkOut,
      ocupacion: {
        adultos: guests,
        ninos: 0,
        infantes: 0,
      },
    };

    console.info('[RoomDetailPage] Creating booking', request);

    this.bookingService.createBooking(request).pipe(
      finalize(() => this.creatingBooking.set(false)),
      catchError((err) => {
        console.error('[RoomDetailPage] createBooking failed', { request, err });
        this.error.set(this.bookingService.getReservationErrorMessage(err));
        return of(null);
      })
    ).subscribe(response => {
      if (!response?.id_reserva) {
        console.error('[RoomDetailPage] createBooking response without id_reserva', response);
        this.error.set(this.bookingService.getReservationErrorMessage(response));
        return;
      }

      console.info('[RoomDetailPage] Booking created, redirecting', response);
      this.router.navigate(['/booking', response.id_reserva]);
    });
  }

  private buildSessionSignature(categoryId: string, checkIn: string, checkOut: string, guests: number): string {
    return [categoryId, checkIn, checkOut, guests].join('|');
  }

  private resolveUserId(): string {
    const key = 'user_id';
    const stored = localStorage.getItem(key);
    if (stored) {
      return stored;
    }
    const generated = crypto.randomUUID();
    localStorage.setItem(key, generated);
    console.warn('[RoomDetailPage] user_id not found in localStorage. Generated temporary UUID.', generated);
    return generated;
  }
}
