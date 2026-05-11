import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute, provideRouter, Router } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';
import { ReservationDetailPage } from './reservation-detail-page';
import { BookingReservation, PaymentInfo } from '../../models/reservation.interface';
import { RoomDetailResponse } from '../../models/room-detail.interface';
import { RoomPriceResponse } from '../../models/room-price.interface';

const USER_ID = 'user-001';
const RESERVATION_ID = 'res-001';
const CATEGORY_ID = 'cat-001';

const mockBooking: BookingReservation = {
  id_reserva: RESERVATION_ID,
  id_usuario: USER_ID,
  id_categoria: CATEGORY_ID,
  estado: 'CONFIRMADA',
  fecha_check_in: '2026-03-07',
  fecha_check_out: '2026-03-10',
  fecha_creacion: '2026-01-01T00:00:00',
  fecha_actualizacion: '2026-01-01T00:00:00',
  codigo_confirmacion_ota: 'TH-001',
  codigo_localizador_pms: '',
  ocupacion: { adultos: 2, ninos: 1, infantes: 0 },
};

const mockCatalogDetail: RoomDetailResponse = {
  propiedad: {
    id_propiedad: 'prop-001',
    nombre: 'Hotel Central',
    estrellas: 4,
    ubicacion: {
      ciudad: 'Bogota',
      estado_provincia: 'Cundinamarca',
      pais: 'Colombia',
      coordenadas: { lat: 4.71, lng: -74.07 },
    },
    porcentaje_impuesto: '19.00',
  },
  categoria: {
    id_categoria: CATEGORY_ID,
    nombre_comercial: 'Suite Deluxe',
    descripcion: 'Habitacion amplia',
    precio_base: {
      monto: '580.00',
      moneda: 'USD',
      cargo_servicio: '0.00',
    },
    capacidad_pax: 3,
    politica_cancelacion: {
      dias_anticipacion: 3,
      porcentaje_penalidad: '50.00',
    },
  },
  amenidades: [],
  galeria: [
    { id_media: 'img-002', url_full: 'https://example.com/2.jpg', tipo: 'FOTO', orden: 2 },
    { id_media: 'img-001', url_full: 'https://example.com/1.jpg', tipo: 'FOTO', orden: 1 },
  ],
  rating_promedio: 4.8,
  total_resenas: 0,
  resenas: [],
};

const mockPayment: PaymentInfo = {
  id_pago: 'pay-001',
  id_reserva: RESERVATION_ID,
  estado: 'APPROVED',
  monto: 580,
  moneda: 'USD',
};

const mockPrice: RoomPriceResponse = {
  precio_por_noche: 180,
  noches: 3,
  subtotal: 540,
  impuestos: 40,
  cargo_servicio: 20,
  total: 600,
  moneda: 'USD',
  simbolo_moneda: '$',
  tipo_tarifa: 'NORMAL',
  impuesto_nombre: 'IVA',
};

describe('ReservationDetailPage', () => {
  let fixture: ComponentFixture<ReservationDetailPage>;
  let component: ReservationDetailPage;
  let httpTesting: HttpTestingController;
  let router: Router;
  let location: Location;

  beforeEach(async () => {
    localStorage.setItem('th_access_token', 'access-token');
    localStorage.setItem('th_refresh_token', 'refresh-token');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'traveler@example.com');
    localStorage.setItem('th_user_id', USER_ID);

    await TestBed.configureTestingModule({
      imports: [ReservationDetailPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: {
            queryParams: of({}),
            snapshot: {
              paramMap: {
                get: (key: string) => key === 'id_reserva' ? RESERVATION_ID : null,
              },
            },
          },
        },
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    spyOn(console, 'info');
    spyOn(console, 'warn');
    spyOn(console, 'error');

    fixture = TestBed.createComponent(ReservationDetailPage);
    component = fixture.componentInstance;
    httpTesting = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);
    location = TestBed.inject(Location);
    fixture.detectChanges();
  });

  afterEach(() => {
    httpTesting.verify();
    localStorage.clear();
  });

  function flushBooking(body: BookingReservation = mockBooking): void {
    const req = httpTesting.expectOne(r => r.url.endsWith(`/reserva/${RESERVATION_ID}`));
    expect(req.request.method).toBe('GET');
    req.flush(body);
  }

  function flushCatalog(body: RoomDetailResponse = mockCatalogDetail): void {
    const req = httpTesting.expectOne(r => r.url.endsWith(`/categories/${CATEGORY_ID}/view-detail`));
    expect(req.request.method).toBe('GET');
    req.flush(body);
    fixture.detectChanges();
  }

  function flushApprovedPayment(body: PaymentInfo = mockPayment): void {
    const req = httpTesting.expectOne(r => r.url.endsWith(`/payments/by-reserva/${RESERVATION_ID}`));
    expect(req.request.method).toBe('GET');
    req.flush(body);
    fixture.detectChanges();
  }

  function flushPaymentError(): void {
    const req = httpTesting.expectOne(r => r.url.endsWith(`/payments/by-reserva/${RESERVATION_ID}`));
    req.flush({ detail: 'Pago no encontrado' }, { status: 404, statusText: 'Not Found' });
  }

  function flushCalculatedPrice(body: RoomPriceResponse = mockPrice): void {
    const req = httpTesting.expectOne(r => r.url.endsWith('/calculate-room-price'));
    expect(req.request.method).toBe('POST');
    req.flush(body);
    fixture.detectChanges();
  }

  it('should show loading while reservation is pending', () => {
    const loading = fixture.nativeElement.querySelector('[data-testid="reservation-detail-loading"]');
    expect(loading).toBeTruthy();
    expect(loading.querySelector('.skeleton-block--hero')).toBeTruthy();
    flushBooking();
    flushCatalog();
    flushApprovedPayment();
  });

  it('should build detail and total from booking, catalog and approved payment', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    expect(component.detail()).toEqual(jasmine.objectContaining({
      id: RESERVATION_ID,
      hotelName: 'Suite Deluxe',
      checkInDate: '2026-03-07',
      checkOutDate: '2026-03-10',
      guests: 3,
      confirmationNumber: 'RES001',
      status: 'CONFIRMADA',
      totalAmount: 580,
      currency: 'USD',
      images: ['https://example.com/1.jpg', 'https://example.com/2.jpg'],
      canCancel: false,
    }));

    const success = fixture.nativeElement.querySelector('[data-testid="reservation-detail-success"]');
    expect(success).toBeTruthy();
    expect(success.textContent).toContain('Suite Deluxe');
    expect(success.textContent).toContain('Bogota, Colombia');
    expect(success.textContent).toMatch(/580/);
    expect(success.textContent).toMatch(/7\s+mar\s+2026/i);
    expect(success.textContent).toContain('10 mar 2026');
    expect(success.textContent).toContain('Confirmada');
  });

  it('should render the required success sections and reservation fields', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-heading"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-image"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-info"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-total"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-actions"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-back"]')).toBeTruthy();

    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-hotel"]').textContent).toContain('Suite Deluxe');
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-location"]').textContent).toContain('Bogota, Colombia');
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-guests"]').textContent).toContain('3');
    const confirmation = fixture.nativeElement.querySelector('[data-testid="reservation-detail-confirmation"]').textContent;
    expect(confirmation).toContain('RES001');
    expect(confirmation).not.toContain('TH-001');
  });

  it('should navigate gallery images with controls and indicators', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    const currentImage = () =>
      fixture.nativeElement.querySelector('[data-testid="reservation-detail-current-image"]') as HTMLImageElement;

    expect(currentImage().src).toContain('/1.jpg');

    const next = fixture.nativeElement.querySelector('[data-testid="gallery-next"]') as HTMLButtonElement;
    next.click();
    fixture.detectChanges();
    expect(component.currentImageIndex()).toBe(1);
    expect(currentImage().src).toContain('/2.jpg');

    const firstIndicator = fixture.nativeElement.querySelectorAll('[data-testid="gallery-indicator"]')[0] as HTMLButtonElement;
    firstIndicator.click();
    fixture.detectChanges();
    expect(component.currentImageIndex()).toBe(0);
    expect(currentImage().src).toContain('/1.jpg');
  });

  it('should show fallback when there are no images', () => {
    flushBooking();
    flushCatalog({ ...mockCatalogDetail, galeria: [] });
    flushApprovedPayment();

    expect(component.currentImageUrl()).toBe('');
    const fallback = fixture.nativeElement.querySelector('[data-testid="reservation-detail-image-fallback"]');
    const controls = fixture.nativeElement.querySelector('[data-testid="gallery-next"]');
    expect(fallback).toBeTruthy();
    expect(controls).toBeNull();
  });

  it('should show fallback when current image fails to load', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    const image = fixture.nativeElement.querySelector('[data-testid="reservation-detail-current-image"]') as HTMLImageElement;
    image.dispatchEvent(new Event('error'));
    fixture.detectChanges();

    expect(component.imageLoadFailed()).toBeTrue();
    const fallback = fixture.nativeElement.querySelector('[data-testid="reservation-detail-image-fallback"]');
    expect(fallback).toBeTruthy();
  });

  it('should use calculated price when payment is not available', () => {
    flushBooking();
    flushCatalog();
    flushPaymentError();
    flushCalculatedPrice();

    expect(component.detail()?.totalAmount).toBe(600);
    expect(component.detail()?.currency).toBe('USD');
    expect(component.totalUnavailable()).toBeFalse();
  });

  it('should enable cancellation and navigate to TODO page when reservation is cancelable', () => {
    spyOn(router, 'navigate').and.resolveTo(true);

    flushBooking({
      ...mockBooking,
      fecha_check_in: '2099-03-07',
      fecha_check_out: '2099-03-10',
    });
    flushCatalog();
    flushApprovedPayment({
      ...mockPayment,
      monto: 580,
    });

    expect(component.detail()?.canCancel).toBeTrue();
    const cancelButton = fixture.nativeElement.querySelector('[data-testid="reservation-detail-cancel"]') as HTMLButtonElement;
    expect(cancelButton.disabled).toBeFalse();

    cancelButton.click();
    expect(router.navigate).toHaveBeenCalledWith(['/mis-reservas', RESERVATION_ID, 'cancelar']);
  });

  it('should disable cancellation and show reason when reservation is not cancelable', () => {
    flushBooking({ ...mockBooking, estado: 'CANCELADA' });
    flushCatalog();
    flushApprovedPayment();

    expect(component.detail()?.canCancel).toBeFalse();
    expect(component.detail()?.cancellationReason).toContain('estado actual');

    const actions = fixture.nativeElement.querySelector('[data-testid="reservation-detail-actions"]');
    const cancelButton = fixture.nativeElement.querySelector('[data-testid="reservation-detail-cancel"]') as HTMLButtonElement;
    expect(cancelButton.disabled).toBeTrue();
    expect(actions.textContent).toContain('estado actual');
  });

  it('should keep detail visible and show total unavailable when payment and price fail', () => {
    flushBooking();
    flushCatalog();
    flushPaymentError();
    const priceReq = httpTesting.expectOne(r => r.url.endsWith('/calculate-room-price'));
    priceReq.flush({ error: 'Server error' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.detail()).not.toBeNull();
    expect(component.detail()?.totalAmount).toBeNull();
    expect(component.totalUnavailable()).toBeTrue();

    const totalUnavailable = fixture.nativeElement.querySelector('[data-testid="reservation-detail-total-unavailable"]');
    expect(totalUnavailable).toBeTruthy();
    expect(totalUnavailable.textContent).toContain('Valor no disponible');
  });

  it('should show unauthorized state when reservation belongs to another user', () => {
    flushBooking({ ...mockBooking, id_usuario: 'other-user' });
    fixture.detectChanges();

    httpTesting.expectNone(r => r.url.includes('/view-detail'));
    expect(component.unauthorized()).toBeTrue();
    expect(component.detail()).toBeNull();

    const unauthorized = fixture.nativeElement.querySelector('[data-testid="reservation-detail-unauthorized"]');
    expect(unauthorized).toBeTruthy();
    expect(unauthorized.textContent).toContain('Volver');
  });

  it('should show not found state when booking API returns 404', () => {
    const req = httpTesting.expectOne(r => r.url.endsWith(`/reserva/${RESERVATION_ID}`));
    req.flush({ error: 'Not found' }, { status: 404, statusText: 'Not Found' });
    fixture.detectChanges();

    expect(component.notFound()).toBeTrue();
    const notFound = fixture.nativeElement.querySelector('[data-testid="reservation-detail-not-found"]');
    expect(notFound).toBeTruthy();
    expect(notFound.textContent).toContain('Reintentar');
    expect(notFound.textContent).toContain('Volver');
  });

  it('should show controlled error when catalog cannot be loaded', () => {
    flushBooking();
    const req = httpTesting.expectOne(r => r.url.endsWith(`/categories/${CATEGORY_ID}/view-detail`));
    req.flush({ error: 'Server error' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.error()).toBe('No pudimos cargar el detalle');
    expect(component.detail()).toBeNull();

    const error = fixture.nativeElement.querySelector('[data-testid="reservation-detail-error"]');
    expect(error).toBeTruthy();
    expect(error.textContent).toContain('Reintentar');
    expect(error.textContent).toContain('Volver');
  });

  it('should retry after a controlled booking error', () => {
    const firstReq = httpTesting.expectOne(r => r.url.endsWith(`/reserva/${RESERVATION_ID}`));
    firstReq.flush({ error: 'Server error' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.error()).toBe('No pudimos cargar el detalle');
    const retryButton = fixture.nativeElement.querySelector('[data-testid="reservation-detail-error"] .state-action') as HTMLButtonElement;
    retryButton.click();
    fixture.detectChanges();

    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    expect(component.error()).toBeNull();
    expect(component.detail()?.id).toBe(RESERVATION_ID);
    expect(fixture.nativeElement.querySelector('[data-testid="reservation-detail-success"]')).toBeTruthy();
  });

  it('should expose empty current image while detail is not loaded', () => {
    expect(component.currentImageUrl()).toBe('');
    flushBooking();
    flushCatalog();
    flushApprovedPayment();
  });

  it('should navigate back with browser history or fallback to reservations list', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    const backSpy = spyOn(location, 'back');
    const navigateSpy = spyOn(router, 'navigate').and.resolveTo(true);
    spyOnProperty(window.history, 'length', 'get').and.returnValues(2, 1);

    (component as any).goBack();
    expect(backSpy).toHaveBeenCalled();

    (component as any).goBack();
    expect(navigateSpy).toHaveBeenCalledWith(['/mis-reservas']);
  });

  it('should wrap gallery navigation and ignore invalid indicators', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    expect(component.currentImageIndex()).toBe(0);

    (component as any).previousImage();
    expect(component.currentImageIndex()).toBe(1);

    (component as any).nextImage();
    expect(component.currentImageIndex()).toBe(0);

    component.currentImageIndex.set(1);
    (component as any).nextImage();
    expect(component.currentImageIndex()).toBe(0);

    (component as any).goToImage(-1);
    expect(component.currentImageIndex()).toBe(0);

    (component as any).goToImage(99);
    expect(component.currentImageIndex()).toBe(0);
  });

  it('should keep gallery guards safe for zero or one image', () => {
    flushBooking();
    flushCatalog({
      ...mockCatalogDetail,
      galeria: [
        { id_media: 'img-001', url_full: 'https://example.com/1.jpg', tipo: 'FOTO', orden: 1 },
      ],
    });
    flushApprovedPayment();

    (component as any).previousImage();
    (component as any).nextImage();
    (component as any).goToImage(1);

    expect(component.currentImageIndex()).toBe(0);
  });

  it('should ignore cancellation start when detail is not available', () => {
    const navigateSpy = spyOn(router, 'navigate').and.resolveTo(true);

    (component as any).startCancellation();

    expect(navigateSpy).not.toHaveBeenCalled();
    flushBooking();
    flushCatalog();
    flushApprovedPayment();
  });

  it('should show controlled error when booking has no category', () => {
    flushBooking({ ...mockBooking, id_categoria: '' });
    fixture.detectChanges();

    httpTesting.expectNone(r => r.url.includes('/view-detail'));
    expect(component.error()).toBe('La reserva solicitada no existe o ya no está disponible.');
    expect(component.detail()).toBeNull();
  });

  it('should build detail with optional catalog and booking fallbacks', () => {
    flushBooking({
      ...mockBooking,
      id_reserva: '',
      ocupacion: undefined,
    } as unknown as BookingReservation);
    flushCatalog({
      ...mockCatalogDetail,
      categoria: {
        ...mockCatalogDetail.categoria,
        politica_cancelacion: undefined,
      } as unknown as RoomDetailResponse['categoria'],
      galeria: undefined,
    } as unknown as RoomDetailResponse);

    const paymentReq = httpTesting.expectOne(r => r.url.endsWith('/payments/by-reserva/'));
    paymentReq.flush({ detail: 'Pago no encontrado' }, { status: 404, statusText: 'Not Found' });
    const priceReq = httpTesting.expectOne(r => r.url.endsWith('/calculate-room-price'));
    priceReq.flush({ error: 'Server error' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.detail()).toEqual(jasmine.objectContaining({
      id: '',
      confirmationNumber: null,
      guests: 0,
      images: [],
      canCancel: false,
    }));
  });

  it('should keep update total and format helpers safe for null values', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    component.detail.set(null);
    (component as any).updateDetailTotal(100, 'USD', 'CONFIRMADA');

    expect(component.detail()).toBeNull();
    expect((component as any).formatCurrency(null, 'USD')).toBe('');
  });

  it('should detect not found errors from generic Error messages', () => {
    flushBooking();
    flushCatalog();
    flushApprovedPayment();

    expect((component as any).isNotFoundError(new Error('404 not found'))).toBeTrue();
    expect((component as any).isNotFoundError(new Error('network'))).toBeFalse();
  });
});
