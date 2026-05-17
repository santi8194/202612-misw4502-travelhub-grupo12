import { provideZonelessChangeDetection } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { ConfirmReservationPage } from './confirm-reservation-page';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../core/services/auth';

const RESERVATION_ID = 'reserva-test-123';
const CATEGORY_ID = 'cat-001';
const PROPERTY_ID = 'prop-001';

const mockBooking: Record<string, any> = {
  id_categoria: CATEGORY_ID,
  estado: 'CONFIRMADA',
  fecha_check_in: '2026-05-01',
  fecha_check_out: '2026-05-05',
  ocupacion: { adultos: 2, ninos: 1, infantes: 0 },
};

const mockCatalog = {
  id_propiedad: PROPERTY_ID,
  propiedad_nombre: 'Hotel Catalogo',
  ciudad: 'Bogota',
  pais: 'Colombia',
  imagen_principal_url: 'https://example.com/catalog.jpg',
  precio_base: '100',
};

const mockCategory = {
  id_propiedad: PROPERTY_ID,
  nombre_comercial: 'Suite Deluxe',
  foto_portada_url: 'https://example.com/category.jpg',
  precio_base: {
    monto: '180',
    moneda: 'USD',
  },
};

const mockProperty = {
  nombre: 'Hotel Central',
  ubicacion: {
    ciudad: 'Bogota',
    pais: 'Colombia',
  },
};

const mockRoomPrice = {
  precio_por_noche: 180,
  noches: 4,
  subtotal: 720,
  impuestos_y_cargos: 90,
  total: 810,
  moneda: 'USD',
  simbolo_moneda: '$',
  impuesto_nombre: 'IVA',
};

describe('ConfirmReservationPage', () => {
  let fixture: ComponentFixture<ConfirmReservationPage>;
  let component: ConfirmReservationPage;
  let httpTesting: HttpTestingController;

  async function setup(
    routeId: string | null = RESERVATION_ID,
    queryParams: Record<string, string> = {
      status: 'confirmed',
      reason: 'Reserva formalizada correctamente',
    },
    sessionEmail: string | null = null,
  ): Promise<void> {
    TestBed.resetTestingModule();

    await TestBed.configureTestingModule({
      imports: [ConfirmReservationPage],
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: convertToParamMap(routeId ? { id_reserva: routeId } : {}),
              queryParamMap: convertToParamMap(queryParams),
            },
          },
        },
        {
          provide: AuthService,
          useValue: {
            getCurrentSession: () => sessionEmail ? { email: sessionEmail } : null,
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ConfirmReservationPage);
    component = fixture.componentInstance;
    httpTesting = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  }

  afterEach(() => {
    httpTesting?.verify();
  });

  function flushBooking(body = mockBooking): void {
    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}`);
    expect(req.request.method).toBe('GET');
    req.flush(body);
  }

  function flushSummaryDependencies(roomPrice: object | null = mockRoomPrice): void {
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`).flush(mockCatalog);
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`).flush(mockCategory);
    httpTesting.expectOne(`${environment.catalogApiUrl}/calculate-room-price`).flush(roomPrice);
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/${PROPERTY_ID}`).flush(mockProperty);
    fixture.detectChanges();
  }

  it('should create', async () => {
    await setup();
    flushBooking();
    flushSummaryDependencies();

    expect(component).toBeTruthy();
  });

  it('should render confirmed reservation state', async () => {
    await setup();
    flushBooking();
    flushSummaryDependencies();

    const title = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-title"]');
    const reason = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-reason"]');
    const confirmationCode = fixture.nativeElement.querySelector('.status-id strong');

    expect(title.textContent).toContain('Reserva Confirmada');
    expect(reason.textContent).toContain('Tu reserva ha sido confirmada. Se ha enviado un correo con los detalles.');
    expect(confirmationCode.textContent).toContain('RESERV');
    expect(confirmationCode.textContent).not.toContain(RESERVATION_ID);
    expect(component.isConfirmed()).toBeTrue();
    expect(component.summary()).toEqual(jasmine.objectContaining({
      propertyName: 'Hotel Central - Suite Deluxe',
      location: 'Bogota, Colombia',
      imageUrl: 'https://example.com/category.jpg',
      guests: 3,
      nights: 4,
      pricePerNight: 180,
      taxesAndFees: 90,
      total: 810,
      currency: 'USD',
      taxesAndFeesLabel: 'IVA y cargos',
    }));
  });

  it('should render rejected reservation state', async () => {
    await setup(RESERVATION_ID, {
      status: 'rejected',
      reason: 'La reserva debe estar en estado HOLD para ser formalizada',
    });
    flushBooking();
    flushSummaryDependencies();

    const title = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-title"]');
    const reason = fixture.nativeElement.querySelector('[data-testid="confirm-reservation-reason"]');

    expect(title.textContent).toContain('Reserva no confirmada');
    expect(reason.textContent).toContain('La reserva debe estar en estado HOLD para ser formalizada');
    expect(component.isConfirmed()).toBeFalse();
  });

  it('should use default rejected status and reason when query params are absent', async () => {
    await setup(RESERVATION_ID, {});
    flushBooking();
    flushSummaryDependencies();

    expect(component.status()).toBe('rejected');
    expect(component.reason()).toContain('No fue posible confirmar');
  });

  it('should stop loading when route has no reservation id', async () => {
    await setup(null);

    expect(component.reservationId()).toBe('');
    expect(component.confirmationCode()).toBe('');
    expect(component.isLoadingSummary()).toBeFalse();
    expect(component.summary()).toBeNull();
  });

  it('should build summary without catalog calls when booking has no category', async () => {
    await setup();
    flushBooking({
      fecha_inicio: '2026-05-01',
      fecha_fin: '2026-05-03',
      num_huespedes: 2,
    });
    fixture.detectChanges();

    httpTesting.expectNone(request => request.url.includes('/categories/'));
    expect(component.summary()).toEqual(jasmine.objectContaining({
      propertyName: 'N/A',
      location: 'N/A, N/A',
      guests: 2,
      nights: 2,
      total: 0,
    }));
  });

  it('should fallback to category price when room price fails', async () => {
    await setup();
    flushBooking({
      ...mockBooking,
      fecha_inicio: '2026-05-01',
      fecha_fin: '2026-05-03',
      num_huespedes: 2,
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`).flush(mockCatalog);
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`).flush({
      ...mockCategory,
      precio_base: undefined,
      monto_precio_base: '150',
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/calculate-room-price`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/${PROPERTY_ID}`).flush(mockProperty);
    fixture.detectChanges();

    expect(component.summary()).toEqual(jasmine.objectContaining({
      guests: 2,
      nights: 2,
      pricePerNight: 150,
      subtotal: 300,
      taxesAndFees: 30,
      total: 330,
      currency: 'COP',
    }));
  });

  it('should fallback to catalog data when category and property are unavailable', async () => {
    await setup();
    flushBooking();
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`).flush({
      ...mockCatalog,
      id_propiedad: undefined,
      nombre: 'Hotel Catalogo',
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/calculate-room-price`).flush(null);
    fixture.detectChanges();

    expect(component.summary()).toEqual(jasmine.objectContaining({
      propertyName: 'Hotel Catalogo',
      location: 'Bogota, Colombia',
      imageUrl: 'https://example.com/catalog.jpg',
      pricePerNight: 100,
      total: 440,
    }));
  });

  it('should fallback when property request fails on both paths', async () => {
    await setup();
    flushBooking();
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`).flush(mockCatalog);
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`).flush(mockCategory);
    httpTesting.expectOne(`${environment.catalogApiUrl}/calculate-room-price`).flush({
      ...mockRoomPrice,
      impuestos_y_cargos: undefined,
      impuestos: 80,
      cargo_servicio: 20,
      total: undefined,
      impuesto_nombre: undefined,
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/${PROPERTY_ID}`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/property/${PROPERTY_ID}`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.summary()).toEqual(jasmine.objectContaining({
      propertyName: 'Hotel Catalogo - Suite Deluxe',
      location: 'Bogota, Colombia',
      taxesAndFees: 100,
      total: 820,
      taxesAndFeesLabel: 'Impuestos y cargos',
    }));
  });

  it('should handle booking load errors as empty summary', async () => {
    await setup();
    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}`);
    req.flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.bookingStatus()).toBe('');
    expect(component.summary()).toBeNull();
    expect(component.isLoadingSummary()).toBeFalse();
  });

  it('should identify cancelled reservations from booking status, query status or reason', async () => {
    await setup(RESERVATION_ID, { status: 'confirmed', reason: 'Reserva formalizada correctamente' });
    flushBooking({ ...mockBooking, estado: 'Cancelada' });
    flushSummaryDependencies();

    expect(component.isCancelled()).toBeTrue();

    await setup(RESERVATION_ID, { status: 'cancelled', reason: 'Reserva formalizada correctamente' });
    flushBooking();
    flushSummaryDependencies();

    expect(component.isCancelled()).toBeTrue();

    await setup(RESERVATION_ID, { status: 'rejected', reason: 'Reserva cancelada por el hotel' });
    flushBooking();
    flushSummaryDependencies();

    expect(component.isCancelled()).toBeTrue();
  });

  it('should return zero nights and guests when dates and occupancy are missing', async () => {
    await setup();
    flushBooking({ id_categoria: CATEGORY_ID });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`).flush(mockCatalog);
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`).flush(mockCategory);
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/${PROPERTY_ID}`).flush(mockProperty);
    fixture.detectChanges();

    expect(component.summary()).toEqual(jasmine.objectContaining({
      checkIn: '',
      checkOut: '',
      guests: 0,
      nights: 0,
      total: 0,
    }));
  });

  it('should show status unavailable alert', async () => {
    await setup(null);
    spyOn(window, 'alert');

    component.showStatusNotAvailableAlert();

    expect(window.alert).toHaveBeenCalledWith('Esta funcionalidad aun no esta disponible.');
  });

  it('should trigger confirmed reservation status email when session email exists', async () => {
    await setup(
      RESERVATION_ID,
      {
        status: 'confirmed',
        reason: 'Reserva formalizada correctamente',
      },
      'viajero@travelhub.com',
    );

    flushBooking({ ...mockBooking, estado: 'CONFIRMADA' });
    flushSummaryDependencies();

    const req = httpTesting.expectOne(
      `${environment.notificationApiUrl}/notifications/reservations/status-email`
    );
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      id_reserva: RESERVATION_ID,
      email_cliente: 'viajero@travelhub.com',
      estado: 'CONFIRMADA',
      codigo_reserva: 'RESERV',
    });
    req.flush({ ok: true });
  });

  it('should include cancellation refund details in status email payload', async () => {
    await setup(
      RESERVATION_ID,
      {
        status: 'rejected',
        reason: 'Reserva cancelada por inventario',
      },
      'viajero@travelhub.com',
    );

    flushBooking({ ...mockBooking, estado: 'CANCELADA' });
    flushSummaryDependencies();

    const previewReq = httpTesting.expectOne(
      `${environment.bookingApiUrl}/${RESERVATION_ID}/cancelacion-preview`
    );
    expect(previewReq.request.method).toBe('GET');
    previewReq.flush({
      refund: {
        expectedRefundAmount: 210,
        currency: 'USD',
        processingTimeLabel: 'Reembolso en 5 dias habiles',
      },
    });

    const req = httpTesting.expectOne(
      `${environment.notificationApiUrl}/notifications/reservations/status-email`
    );
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      id_reserva: RESERVATION_ID,
      email_cliente: 'viajero@travelhub.com',
      estado: 'CANCELADA',
      monto_reembolso: 210,
      moneda_reembolso: 'USD',
      detalle_reembolso: 'Reembolso en 5 dias habiles',
    });
    req.flush({ ok: true });
  });
});
