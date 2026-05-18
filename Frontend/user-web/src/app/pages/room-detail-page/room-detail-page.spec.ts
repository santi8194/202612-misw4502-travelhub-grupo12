import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { ActivatedRoute, provideRouter, Router } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { of } from 'rxjs';
import { RoomDetailPage } from './room-detail-page';
import { NotificationService } from '../../core/services/notification';
import { BookingStore } from '../../core/store/booking-store';
import { I18nService } from '../../core/i18n/i18n.service';
import { RoomDetailResponse } from '../../models/room-detail.interface';
import { RoomPriceResponse } from '../../models/room-price.interface';

const mockRoomDetail: RoomDetailResponse = {
  propiedad: {
    id_propiedad: '8f967297-8b18-40e4-b410-cd3c36fa2eb6',
    nombre: 'Cabaña',
    estrellas: 2,
    ubicacion: {
      ciudad: 'Bogotá',
      estado_provincia: 'Cundinamarca',
      pais: 'Colombia',
      coordenadas: { lat: 4.5982, lng: -74.0531 },
    },
    porcentaje_impuesto: '19.00',
  },
  categoria: {
    id_categoria: '7723e55e-6a70-4f25-9bb6-092d9b0e583d',
    nombre_comercial: 'Cabaña Eco Bogotá 0',
    descripcion: 'Confortable opción en Bogotá',
    precio_base: {
      monto: '374000.00',
      moneda: 'COP',
      cargo_servicio: '0.00',
    },
    capacidad_pax: 4,
    politica_cancelacion: {
      dias_anticipacion: 3,
      porcentaje_penalidad: '50.00',
    },
  },
  amenidades: [
    { id_amenidad: 'amenity-pool', nombre: 'Piscina', icono: 'pool-icon' },
    { id_amenidad: 'amenity-spa', nombre: 'Spa', icono: 'spa-icon' },
  ],
  galeria: [
    {
      id_media: 'd95a5b81-8301-4949-ba1a-57c4ac7674a2',
      url_full: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80',
      tipo: 'FOTO_PORTADA',
      orden: 1,
    },
  ],
  rating_promedio: 4.0,
  total_resenas: 3,
  resenas: [
    {
      id_resena: '60a506d2-8daa-43ff-ad66-849daf2be7f5',
      id_usuario: 'ea16ea64-45cf-47d7-93f1-5513c2963d21',
      nombre_autor: 'Jorge Silva',
      avatar_url: 'https://ui-avatars.com/api/?name=Jorge+Silva',
      calificacion: 4,
      comentario: 'Excelente servicio y ubicación.',
      fecha_creacion: '2026-04-19T00:31:33+00:00',
    },
    {
      id_resena: 'b0003c98-1d80-41f9-bc17-9ee5241dbb2a',
      id_usuario: '91499d9c-b934-45cc-bff6-45e05730795a',
      nombre_autor: 'María Camila',
      avatar_url: 'https://ui-avatars.com/api/?name=María+Camila',
      calificacion: 5,
      comentario: 'Excelente servicio y ubicación.',
      fecha_creacion: '2026-04-19T00:31:33+00:00',
    },
  ],
};

const mockRoomPrice: RoomPriceResponse = {
  precio_por_noche: 374000,
  noches: 3,
  subtotal: 1122000,
  impuestos: 213180,
  cargo_servicio: 20000,
  total: 1355180,
  moneda: 'COP',
  simbolo_moneda: '$',
  tipo_tarifa: 'NORMAL',
  impuesto_nombre: 'IVA',
};

const CATALOG_VIEW_DETAIL_URL_PATTERN = /\/categories\/[^/]+\/view-detail/;
const CALCULATE_PRICE_URL_PATTERN = /\/calculate-room-price/;
const USER_LOCALE_URL_PATTERN = /\/assets\/data\/user-locale\.json/;
const BOOKING_URL_PATTERN = /\/api\/reserva/;

describe('RoomDetailPage', () => {
  let component: RoomDetailPage;
  let fixture: ComponentFixture<RoomDetailPage>;
  let httpTesting: HttpTestingController;
  let notificationService: NotificationService;
  let bookingStore: BookingStore;

  beforeEach(async () => {
    localStorage.removeItem('th_language');

    await TestBed.configureTestingModule({
      imports: [RoomDetailPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([
          { path: 'category/:category_id', component: RoomDetailPage },
          { path: 'booking/:id_reserva', component: RoomDetailPage }, // stub for redirect
          { path: 'auth/login', component: RoomDetailPage },
        ]),
        {
          provide: ActivatedRoute,
          useValue: {
            queryParams: of({}),
            snapshot: {
              paramMap: {
                get: (key: string) => key === 'category_id' ? '7723e55e-6a70-4f25-9bb6-092d9b0e583d' : null
              },
              queryParamMap: {
                get: (key: string) => null
              }
            }
          }
        },
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    spyOn(console, 'info');
    spyOn(console, 'warn');
    spyOn(console, 'error');

    fixture = TestBed.createComponent(RoomDetailPage);
    component = fixture.componentInstance;
    httpTesting = TestBed.inject(HttpTestingController);
    notificationService = TestBed.inject(NotificationService);
    bookingStore = TestBed.inject(BookingStore);

    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'juan@ejemplo.com');
    localStorage.setItem('th_user_id', 'test-user-uuid');

    fixture.detectChanges();
  });

  afterEach(() => {
    httpTesting.verify();
    localStorage.clear();
  });

  // ── Helpers ──
  function flushUserLocale(): void {
    const req = httpTesting.match(r => USER_LOCALE_URL_PATTERN.test(r.url));
    req.forEach(r => r.flush({ pais: 'Colombia' }));
  }

  function flushViewDetail(body: RoomDetailResponse = mockRoomDetail): void {
    const req = httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url));
    req.flush(body);
    fixture.detectChanges();
  }

  function flushPendingViewDetail(body: RoomDetailResponse = mockRoomDetail): void {
    const reqs = httpTesting.match(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url));
    reqs.forEach(req => req.flush(body));
    fixture.detectChanges();
  }

  function flushViewDetailError(status = 500): void {
    const req = httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url));
    req.flush({ message: 'Server error' }, { status, statusText: 'Error' });
    fixture.detectChanges();
  }

  function flushCalculatePrice(body: RoomPriceResponse = mockRoomPrice): void {
    const req = httpTesting.expectOne(r => CALCULATE_PRICE_URL_PATTERN.test(r.url));
    req.flush(body);
    fixture.detectChanges();
  }

  // ── Tests ──

  it('should create', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    expect(component).toBeTruthy();
  });

  it('should render app-header', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    fixture.detectChanges();
    const header = fixture.nativeElement.querySelector('app-header');
    expect(header).toBeTruthy();
  });

  it('should render app-footer', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    fixture.detectChanges();
    const footer = fixture.nativeElement.querySelector('app-footer');
    expect(footer).toBeTruthy();
  });

  it('should show loading state initially before API responds', () => {
    const loading = fixture.nativeElement.querySelector('[data-testid="room-detail-loading"]');
    expect(loading).toBeTruthy();
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
  });

  it('should show error state when API fails', () => {
    flushUserLocale();
    flushViewDetailError(500);
    const error = fixture.nativeElement.querySelector('[data-testid="room-detail-error"]');
    expect(error).toBeTruthy();
    expect(error.textContent).toContain('No fue posible cargar el detalle de la habitación');
  });

  it('should render room title with nombre_comercial on success', () => {
    flushUserLocale();
    flushViewDetail();
    const title = fixture.nativeElement.querySelector('[data-testid="room-detail-title"]');
    expect(title).toBeTruthy();
    expect(title.textContent.trim()).toContain('Cabaña Eco Bogotá 0');
  });

  it('should translate backend property type label in title when language is en', () => {
    flushUserLocale();
    const fincaRoomDetail: RoomDetailResponse = {
      ...mockRoomDetail,
      categoria: {
        ...mockRoomDetail.categoria,
        nombre_comercial: 'Finca',
      },
    };
    flushViewDetail(fincaRoomDetail);

    TestBed.inject(I18nService).setLanguage('en');
    fixture.detectChanges();
    flushPendingViewDetail(fincaRoomDetail);
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector('[data-testid="room-detail-title"]');
    expect(title.textContent.trim()).toBe('Country house');
  });

  it('should render image grid on success', () => {
    flushUserLocale();
    flushViewDetail();
    const grid = fixture.nativeElement.querySelector('[data-testid="room-image-grid"]');
    expect(grid).toBeTruthy();
  });

  it('should render amenities section', () => {
    flushUserLocale();
    flushViewDetail();
    const amenities = fixture.nativeElement.querySelector('[data-testid="room-amenities"]');
    expect(amenities).toBeTruthy();
    const items = fixture.nativeElement.querySelectorAll('[data-testid="room-amenity-item"]');
    expect(items.length).toBe(mockRoomDetail.amenidades.length);
  });

  it('should render booking box on success', () => {
    flushUserLocale();
    flushViewDetail();
    const bookingBox = fixture.nativeElement.querySelector('[data-testid="room-booking-box"]');
    expect(bookingBox).toBeTruthy();
  });

  it('should render reviews section with all reseñas', () => {
    flushUserLocale();
    flushViewDetail();
    const reviews = fixture.nativeElement.querySelector('[data-testid="room-reviews"]');
    expect(reviews).toBeTruthy();
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="room-review-card"]');
    expect(cards.length).toBe(mockRoomDetail.resenas.length);
  });

  it('should render cancellation policy section', () => {
    flushUserLocale();
    flushViewDetail();
    const policies = fixture.nativeElement.querySelector('[data-testid="room-policies"]');
    expect(policies).toBeTruthy();
  });

  it('should render reviews, policies and amenity labels in English when language is en', () => {
    flushUserLocale();
    flushViewDetail();

    TestBed.inject(I18nService).setLanguage('en');
    fixture.detectChanges();
    flushPendingViewDetail();
    fixture.detectChanges();

    const reviewsCount = fixture.nativeElement.querySelector('.reviews-header__count');
    expect(reviewsCount.textContent).toContain('reviews');

    const policyTitle = fixture.nativeElement.querySelector('.policy-item__title');
    expect(policyTitle.textContent).toContain('Cancellation policy');

    const amenityName = fixture.nativeElement.querySelector('.amenity-item__name');
    expect(amenityName.textContent).toContain('Pool');
  });

  it('should calculate nightsCount correctly', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    component.checkInInput.set('2026-01-01');
    component.checkOutInput.set('2026-01-08');
    expect(component.nightsCount()).toBe(7);
  });

  it('should return subtotal from roomPrice when available', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    component.roomPrice.set(mockRoomPrice);
    expect(component.subtotal()).toBe(mockRoomPrice.subtotal);
  });

  it('should return total from roomPrice when available', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    component.roomPrice.set(mockRoomPrice);
    expect(component.total()).toBe(mockRoomPrice.total);
  });

  it('should return pricePerNight from roomDetail fallback when roomPrice is null', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    expect(component.roomPrice()).toBeNull();
    expect(component.pricePerNight()).toBe(374000);
  });

  it('should have canReserve false when dates are missing', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    component.checkInInput.set('');
    component.checkOutInput.set('');
    expect(component.canReserve()).toBeFalse();
  });

  it('should have canReserve true when form is valid', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-05');
    component.guestsInput.set(2);
    expect(component.canReserve()).toBeTrue();
  });

  it('should render price breakdown with impuestos and cargo_servicio when roomPrice is set', () => {
    flushUserLocale();
    flushViewDetail();
    component.roomPrice.set(mockRoomPrice);
    fixture.detectChanges();
    const breakdown = fixture.nativeElement.querySelector('[data-testid="room-price-breakdown"]');
    expect(breakdown).toBeTruthy();
    const impuestosRow = fixture.nativeElement.querySelector('[data-testid="room-impuestos-row"]');
    expect(impuestosRow).toBeTruthy();
    expect(impuestosRow.textContent).toContain('IVA');
    const cargoRow = fixture.nativeElement.querySelector('[data-testid="room-cargo-servicio-row"]');
    expect(cargoRow).toBeTruthy();
    expect(cargoRow.textContent).toContain('Tarifa del servicio');
  });

  it('should render loading shimmer in breakdown while loadingPrice is true', () => {
    flushUserLocale();
    flushViewDetail();
    component.loadingPrice.set(true);
    fixture.detectChanges();
    const loadingEl = fixture.nativeElement.querySelector('[data-testid="room-price-loading"]');
    expect(loadingEl).toBeTruthy();
    const breakdown = fixture.nativeElement.querySelector('[data-testid="room-price-breakdown"]');
    expect(breakdown).toBeNull();
  });

  it('date inputs should have readonly attribute', () => {
    flushUserLocale();
    flushViewDetail();
    const checkIn = fixture.nativeElement.querySelector('[data-testid="room-checkin"]');
    const checkOut = fixture.nativeElement.querySelector('[data-testid="room-checkout"]');
    const guests = fixture.nativeElement.querySelector('[data-testid="room-guests"]');
    expect(checkIn.readOnly).toBeTrue();
    expect(checkOut.readOnly).toBeTrue();
    expect(guests.readOnly).toBeTrue();
  });

  it('should call createBooking with correct payload on reservar()', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    fixture.detectChanges();

    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');
    component.guestsInput.set(2);

    component.reservar();
    fixture.detectChanges();

    const bookingReq = httpTesting.expectOne(r => BOOKING_URL_PATTERN.test(r.url));
    expect(bookingReq.request.method).toBe('POST');
    expect(bookingReq.request.body.fecha_check_in).toBe('2026-06-01');
    expect(bookingReq.request.body.fecha_check_out).toBe('2026-06-03');
    expect(bookingReq.request.body.ocupacion.adultos).toBe(2);
    expect(bookingReq.request.body.id_usuario).toBe('test-user-uuid');
    expect(bookingReq.request.body.usuario_email).toBe('juan@ejemplo.com');

    bookingReq.flush({ id_reserva: 'reserva-test-001' });
  });

  it('should navigate to /booking/:id_reserva after successful createBooking', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    fixture.detectChanges();

    const navigateSpy = spyOn((component as any).router, 'navigate');

    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');
    component.guestsInput.set(1);

    component.reservar();
    fixture.detectChanges();

    const bookingReq = httpTesting.expectOne(r => BOOKING_URL_PATTERN.test(r.url));
    bookingReq.flush({ id_reserva: 'reserva-test-001' });
    fixture.detectChanges();

    expect(navigateSpy).toHaveBeenCalledWith(['/booking', 'reserva-test-001']);
  });

  it('should require login before creating a reservation', () => {
    flushUserLocale();
    httpTesting.expectOne(r => CATALOG_VIEW_DETAIL_URL_PATTERN.test(r.url)).flush(mockRoomDetail);
    fixture.detectChanges();

    const navigateSpy = spyOn(TestBed.inject(Router), 'navigate');
    const notificationSpy = spyOn(notificationService, 'showError');

    localStorage.clear();
    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');
    component.guestsInput.set(2);

    component.reservar();
    fixture.detectChanges();

    httpTesting.expectNone(r => BOOKING_URL_PATTERN.test(r.url));
    expect(component.error()).toBe('No se pudo iniciar sesión. Verifica tus credenciales e intenta nuevamente.');
    expect(notificationSpy).toHaveBeenCalledWith('No se pudo iniciar sesión. Verifica tus credenciales e intenta nuevamente.');
    expect(navigateSpy).toHaveBeenCalledWith(['/auth/login'], {
      queryParams: { redirect: '/' },
    });
  });

  it('should return zero nights for missing or reversed dates', () => {
    flushUserLocale();
    flushViewDetail();

    component.checkInInput.set('');
    component.checkOutInput.set('2026-06-03');
    expect(component.nightsCount()).toBe(0);

    component.checkInInput.set('2026-06-05');
    component.checkOutInput.set('2026-06-03');
    expect(component.nightsCount()).toBe(0);
  });

  it('should use room price, invalid fallback and currency branches', () => {
    flushUserLocale();
    flushViewDetail({
      ...mockRoomDetail,
      categoria: {
        ...mockRoomDetail.categoria,
        precio_base: {
          ...mockRoomDetail.categoria.precio_base,
          monto: 'no-es-numero',
          moneda: 'USD',
        },
      },
    });

    expect(component.pricePerNight()).toBe(0);
    expect(component.currencySymbol()).toBe('$');

    component.roomPrice.set({
      ...mockRoomPrice,
      precio_por_noche: 410000,
      simbolo_moneda: '€',
    });

    expect(component.pricePerNight()).toBe(410000);
    expect(component.currencySymbol()).toBe('€');
  });

  it('should resolve taxes, service fee and tax label fallback branches', () => {
    flushUserLocale();
    flushViewDetail();

    expect(component.impuestos()).toBe(0);
    expect(component.cargoServicio()).toBe(0);
    expect(component.impuestoNombre()).toBe('IVA');

    component.roomPrice.set({
      ...mockRoomPrice,
      impuestos_y_cargos: 12000,
      impuestos: undefined,
      cargo_servicio: 9000,
      impuesto_nombre: undefined,
    } as unknown as RoomPriceResponse);

    expect(component.impuestos()).toBe(12000);
    expect(component.cargoServicio()).toBe(0);
    expect(component.impuestoNombre()).toBe('IVA');

    component.roomPrice.set({
      ...mockRoomPrice,
      impuestos: undefined,
      cargo_servicio: undefined,
    } as unknown as RoomPriceResponse);

    expect(component.impuestos()).toBe(0);
    expect(component.cargoServicio()).toBe(0);
  });

  it('should build gallery placeholders, sorted repeated images and short descriptions', () => {
    flushUserLocale();
    flushViewDetail({
      ...mockRoomDetail,
      categoria: {
        ...mockRoomDetail.categoria,
        descripcion: 'x'.repeat(245),
      },
      galeria: [
        { id_media: '2', url_full: 'https://example.com/segunda.jpg', tipo: 'FOTO', orden: 2 },
        { id_media: '1', url_full: 'https://example.com/primera.jpg', tipo: 'FOTO', orden: 1 },
      ],
    });

    expect(component.galleryImages()).toEqual([
      'https://example.com/primera.jpg',
      'https://example.com/segunda.jpg',
      'https://example.com/segunda.jpg',
      'https://example.com/segunda.jpg',
      'https://example.com/segunda.jpg',
    ]);
    expect(component.shortDescription()).toBe(`${'x'.repeat(240)}...`);

    component.roomDetail.set({ ...mockRoomDetail, galeria: [] });

    expect(component.galleryImages()).toEqual(['', '', '', '', '']);
  });

  it('should format empty dates, zero currency and unknown amenity icons', () => {
    flushUserLocale();
    flushViewDetail();

    expect(component.formatDate('')).toBe('');
    expect(component.formatCurrency(0)).toBe('0');
    expect(component.formatCurrency(1234567)).toBe('1.234.567');
    expect(component.getAmenityIcon('unknown-icon')).toBe(component.amenityIconSvg['default']);
  });

  it('should toggle long description state', () => {
    flushUserLocale();
    flushViewDetail();

    expect(component.descriptionExpanded()).toBeFalse();
    component.toggleDescription();
    expect(component.descriptionExpanded()).toBeTrue();
    component.toggleDescription();
    expect(component.descriptionExpanded()).toBeFalse();
  });

  it('should handle user locale load errors with the default country', () => {
    const req = httpTesting.expectOne(r => USER_LOCALE_URL_PATTERN.test(r.url));
    req.flush({}, { status: 404, statusText: 'Not Found' });
    flushViewDetail();

    expect(component.paisUsuario()).toBe('Colombia');
  });

  it('should calculate price only when dates are valid', () => {
    flushUserLocale();
    flushViewDetail();

    (component as any).calculatePrice();
    httpTesting.expectNone(r => CALCULATE_PRICE_URL_PATTERN.test(r.url));

    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');

    (component as any).calculatePrice();

    const priceReq = httpTesting.expectOne(r => CALCULATE_PRICE_URL_PATTERN.test(r.url));
    expect(priceReq.request.body).toEqual({
      id_categoria: '7723e55e-6a70-4f25-9bb6-092d9b0e583d',
      fecha_inicio: '2026-06-01',
      fecha_fin: '2026-06-03',
      pais_usuario: 'Colombia',
    });

    priceReq.flush(mockRoomPrice);
    expect(component.roomPrice()).toEqual(mockRoomPrice);
    expect(component.loadingPrice()).toBeFalse();
  });

  it('should keep the page usable when price calculation fails', () => {
    flushUserLocale();
    flushViewDetail();

    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');

    (component as any).calculatePrice();

    const priceReq = httpTesting.expectOne(r => CALCULATE_PRICE_URL_PATTERN.test(r.url));
    priceReq.flush({ message: 'Price error' }, { status: 500, statusText: 'Error' });

    expect(component.roomPrice()).toBeNull();
    expect(component.loadingPrice()).toBeFalse();
  });

  it('should block booking when required data is invalid', () => {
    flushUserLocale();
    flushViewDetail();

    component.checkInInput.set('2026-06-03');
    component.checkOutInput.set('2026-06-01');
    component.guestsInput.set(2);

    component.reservar();

    httpTesting.expectNone(r => BOOKING_URL_PATTERN.test(r.url));
    expect(component.error()).toBe('La reserva no tiene todos los datos necesarios para continuar con el pago.');
  });

  it('should redirect to existing active booking session', () => {
    flushUserLocale();
    flushViewDetail();

    const navigateSpy = spyOn(TestBed.inject(Router), 'navigate');
    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');
    component.guestsInput.set(2);

    bookingStore.setBookingSession(
      '7723e55e-6a70-4f25-9bb6-092d9b0e583d|2026-06-01|2026-06-03|2',
      {
        reservationId: 'reserva-activa',
        signature: '7723e55e-6a70-4f25-9bb6-092d9b0e583d|2026-06-01|2026-06-03|2',
        expiresAt: Date.now() + 60000,
      }
    );

    component.reservar();

    httpTesting.expectNone(r => BOOKING_URL_PATTERN.test(r.url));
    expect(navigateSpy).toHaveBeenCalledWith(['/existing-session-redirect'], {
      queryParams: { reservationId: 'reserva-activa' },
    });
  });

  it('should clear expired session and create a new booking', () => {
    flushUserLocale();
    flushViewDetail();

    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');
    component.guestsInput.set(2);

    const signature = '7723e55e-6a70-4f25-9bb6-092d9b0e583d|2026-06-01|2026-06-03|2';
    bookingStore.setBookingSession(signature, {
      reservationId: 'reserva-expirada',
      signature,
      expiresAt: Date.now() - 1000,
    });

    component.reservar();

    expect(bookingStore.getBookingSession(signature)).toBeNull();
    const bookingReq = httpTesting.expectOne(r => BOOKING_URL_PATTERN.test(r.url));
    bookingReq.flush({ id_reserva: 'reserva-nueva' });
  });

  it('should show a controlled error when booking response has no id_reserva', () => {
    flushUserLocale();
    flushViewDetail();

    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');
    component.guestsInput.set(2);

    component.reservar();

    const bookingReq = httpTesting.expectOne(r => BOOKING_URL_PATTERN.test(r.url));
    bookingReq.flush({});

    expect(component.error()).toBe('No fue posible crear la reserva. Intenta nuevamente.');
    expect(component.creatingBooking()).toBeFalse();
  });

  it('should show mapped booking errors when createBooking fails', () => {
    flushUserLocale();
    flushViewDetail();

    component.checkInInput.set('2026-06-01');
    component.checkOutInput.set('2026-06-03');
    component.guestsInput.set(2);

    component.reservar();

    const bookingReq = httpTesting.expectOne(r => BOOKING_URL_PATTERN.test(r.url));
    bookingReq.flush(
      { detail: { code: 'BOOKING_HOLD_ALREADY_ACTIVE' } },
      { status: 409, statusText: 'Conflict' }
    );

    expect(component.error()).toBe('No fue posible crear la reserva. Intenta nuevamente.');
    expect(component.creatingBooking()).toBeFalse();
  });
});
