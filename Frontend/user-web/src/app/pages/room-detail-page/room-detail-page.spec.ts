import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { ActivatedRoute, provideRouter, Router } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { of } from 'rxjs';
import { RoomDetailPage } from './room-detail-page';
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

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoomDetailPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([
          { path: 'category/:category_id', component: RoomDetailPage },
          { path: 'booking/:id_reserva', component: RoomDetailPage }, // stub for redirect
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

    fixture = TestBed.createComponent(RoomDetailPage);
    component = fixture.componentInstance;
    httpTesting = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => httpTesting.verify());

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

    spyOn(component as any, 'resolveUserId').and.returnValue('test-user-uuid');

    component.reservar();
    fixture.detectChanges();

    const bookingReq = httpTesting.expectOne(r => BOOKING_URL_PATTERN.test(r.url));
    expect(bookingReq.request.method).toBe('POST');
    expect(bookingReq.request.body.fecha_check_in).toBe('2026-06-01');
    expect(bookingReq.request.body.fecha_check_out).toBe('2026-06-03');
    expect(bookingReq.request.body.ocupacion.adultos).toBe(2);

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
    spyOn(component as any, 'resolveUserId').and.returnValue('test-user-uuid');

    component.reservar();
    fixture.detectChanges();

    const bookingReq = httpTesting.expectOne(r => BOOKING_URL_PATTERN.test(r.url));
    bookingReq.flush({ id_reserva: 'reserva-test-001' });
    fixture.detectChanges();

    expect(navigateSpy).toHaveBeenCalledWith(['/booking', 'reserva-test-001']);
  });
});
