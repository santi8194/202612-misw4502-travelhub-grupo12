import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { Location } from '@angular/common';
import { provideHttpClient } from '@angular/common/http';
import { ActivatedRoute, Router, convertToParamMap, provideRouter } from '@angular/router';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { BookingCartPage } from './booking-cart-page';
import { environment } from '../../../environments/environment';

const RESERVATION_ID = 'reserva-test-001';
const CATEGORY_ID = 'cat-001';
const PROPERTY_ID = 'prop-001';

const mockBooking: Record<string, any> = {
  id_usuario: 'user-001',
  id_categoria: CATEGORY_ID,
  fecha_check_in: '2026-05-01',
  fecha_check_out: '2026-05-05',
  ocupacion: { adultos: 2, ninos: 1, infantes: 0 },
};

const mockCatalog = {
  id_propiedad: PROPERTY_ID,
  nombre: 'Hotel Catalogo',
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
  id_propiedad: PROPERTY_ID,
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
  impuestos: 80,
  cargo_servicio: 20,
  total: 820,
  moneda: 'USD',
  simbolo_moneda: '$',
  tipo_tarifa: 'NORMAL',
  impuesto_nombre: 'IVA',
};

describe('BookingCartPage', () => {
  let component: BookingCartPage;
  let fixture: ComponentFixture<BookingCartPage>;
  let httpTesting: HttpTestingController;
  let router: Router;
  let location: Location;

  async function setup(routeId: string | null = null) {
    localStorage.clear();
    sessionStorage.clear();
    TestBed.resetTestingModule();

    await TestBed.configureTestingModule({
      imports: [BookingCartPage],
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
            },
          },
        },
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(BookingCartPage);
    component = fixture.componentInstance;
    httpTesting = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);
    location = TestBed.inject(Location);
    fixture.detectChanges();
  }

  afterEach(() => {
    httpTesting?.verify();
    component?.ngOnDestroy();
    localStorage.clear();
    sessionStorage.clear();
  });

  function flushBooking(body = mockBooking): void {
    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}`);
    expect(req.request.method).toBe('GET');
    req.flush(body);
  }

  function flushSummaryDependencies(): void {
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`).flush(mockCatalog);
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`).flush(mockCategory);
    httpTesting.expectOne(`${environment.catalogApiUrl}/calculate-room-price`).flush(mockRoomPrice);
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/${PROPERTY_ID}`).flush(mockProperty);
    fixture.detectChanges();
  }

  function flushSummaryDependenciesWithoutPrice(): void {
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`).flush(mockCatalog);
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`).flush(mockCategory);
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/${PROPERTY_ID}`).flush(mockProperty);
    fixture.detectChanges();
  }

  function completeGuestForm(): void {
    component.form.set({
      name: 'Ana',
      lastName: 'Perez',
      email: 'ana@example.com',
      phone: '3001234567',
      detailedRequest: 'Sin solicitudes',
    });
  }

  it('should create', async () => {
    await setup();
    expect(component).toBeTruthy();
  });

  it('should initialize form with empty values', async () => {
    await setup();
    const form = component.form();
    expect(form.name).toBe('');
    expect(form.lastName).toBe('');
    expect(form.email).toBe('');
    expect(form.phone).toBe('');
    expect(form.detailedRequest).toBe('');
  });

  it('should have timer active after initialization', async () => {
    await setup();
    expect(component.timerActive()).toBeTrue();
    expect(component.remainingTime()).toBeGreaterThan(0);
  });

  it('should render the continue button', async () => {
    await setup();
    const btn = fixture.nativeElement.querySelector('[data-testid="continue-payment-btn"]');
    expect(btn).toBeTruthy();
    expect(btn.textContent.trim()).toContain('Continuar con el pago');
  });

  it('should render the inline error message when hold creation fails', async () => {
    await setup();
    component.holdError.set('La categoria seleccionada no existe o ya no esta disponible.');

    fixture.detectChanges();

    const error = fixture.nativeElement.querySelector('[data-testid="booking-cart-error"]');
    expect(error).toBeTruthy();
    expect(error.textContent).toContain('La categoria seleccionada no existe o ya no esta disponible.');
  });

  it('should hide hold timer when redirecting to an existing session', async () => {
    await setup();
    component.isRedirectingToExistingSession.set(true);
    component.remainingTime.set(120);

    fixture.detectChanges();

    const timer = fixture.nativeElement.querySelector('[data-testid="hold-timer"]');
    expect(timer).toBeNull();
  });

  it('should load summary from booking, catalog, category, price and property', async () => {
    await setup(RESERVATION_ID);

    flushBooking();
    flushSummaryDependencies();

    expect(component.summary()).toEqual(jasmine.objectContaining({
      propertyName: 'Hotel Central - Suite Deluxe',
      location: 'Bogota, Colombia',
      imageUrl: 'https://example.com/category.jpg',
      checkIn: '2026-05-01',
      checkOut: '2026-05-05',
      guests: 3,
      nights: 4,
      total: 820,
      currency: 'USD',
      taxesAndFeesLabel: 'IVA y cargos',
    }));
    expect(component.isLoadingSummary()).toBeFalse();
  });

  it('should build fallback summary when optional catalog requests fail', async () => {
    await setup(RESERVATION_ID);

    flushBooking({
      ...mockBooking,
      fecha_inicio: '2026-05-01',
      fecha_fin: '2026-05-03',
      num_huespedes: 2,
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/${CATEGORY_ID}`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/${CATEGORY_ID}`)
      .flush({ ...mockCategory, precio_base: undefined, monto_precio_base: '150' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/calculate-room-price`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/${PROPERTY_ID}`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/property/${PROPERTY_ID}`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.summary()).toEqual(jasmine.objectContaining({
      propertyName: 'N/A - Suite Deluxe',
      location: 'N/A, N/A',
      guests: 2,
      nights: 2,
      pricePerNight: 150,
      subtotal: 300,
      taxesAndFees: 30,
      total: 330,
      currency: 'COP',
    }));
  });

  it('should not request catalog when booking has no category', async () => {
    await setup(RESERVATION_ID);

    flushBooking({ ...mockBooking, id_categoria: undefined });
    fixture.detectChanges();

    httpTesting.expectNone(request => request.url.includes('/categories/'));
    expect(component.summary()?.propertyName).toBe('N/A');
    expect(component.summary()?.total).toBe(0);
  });

  it('should show no summary when booking cannot be loaded', async () => {
    await setup(RESERVATION_ID);

    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}`);
    req.flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();

    expect(component.summary()).toBeNull();
    expect(component.isLoadingSummary()).toBeFalse();
  });

  it('should update form fields from direct calls and events', async () => {
    await setup();

    component.updateField('name', 'Ana');
    component.onFieldChange({ field: 'email', value: 'ana@example.com' });

    expect(component.form().name).toBe('Ana');
    expect(component.form().email).toBe('ana@example.com');
  });

  it('should validate guest form completion and email format', async () => {
    await setup();

    component.form.set({
      name: 'Ana',
      lastName: 'Perez',
      email: 'invalid',
      phone: '300',
      detailedRequest: '',
    });
    expect(component.isGuestFormComplete()).toBeFalse();

    component.updateField('email', 'ana@example.com');
    expect(component.isGuestFormComplete()).toBeTrue();
  });

  it('should block hold creation when form is incomplete', async () => {
    await setup(RESERVATION_ID);
    flushBooking();
    flushSummaryDependencies();

    component.createHold();

    expect(component.holdError()).toContain('Completa');
  });

  it('should block hold creation when timer has expired', async () => {
    await setup(RESERVATION_ID);
    spyOn(window, 'alert');
    flushBooking();
    flushSummaryDependencies();
    completeGuestForm();
    component.remainingTime.set(0);

    component.createHold();

    expect(component.holdError()).toContain('El tiempo de hold');
    expect(window.alert).toHaveBeenCalled();
  });

  it('should block hold creation when reservation id is missing', async () => {
    await setup();
    completeGuestForm();

    component.createHold();

    expect(component.holdError()).toContain('identificador');
  });

  it('should block hold creation when booking data is missing', async () => {
    await setup(RESERVATION_ID);
    spyOn(window, 'alert');
    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}`);
    req.flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    fixture.detectChanges();
    completeGuestForm();

    component.createHold();

    expect(component.holdError()).toContain('No se pudo cargar la reserva');
    expect(window.alert).toHaveBeenCalledWith('No se pudo cargar la reserva desde backend');
  });

  it('should block hold creation when backend booking data is incomplete', async () => {
    await setup(RESERVATION_ID);
    spyOn(window, 'alert');
    flushBooking({ ...mockBooking, fecha_check_in: '', fecha_check_out: '' });
    flushSummaryDependenciesWithoutPrice();
    completeGuestForm();

    component.createHold();

    expect(component.holdError()).toContain('La reserva no tiene todos los datos necesarios');
    expect(window.alert).toHaveBeenCalled();
  });

  it('should block hold creation when total is not available', async () => {
    await setup(RESERVATION_ID);
    flushBooking();
    flushSummaryDependencies();
    completeGuestForm();
    component.summary.set({ ...component.summary()!, total: 0 });

    component.createHold();

    expect(component.holdError()).toContain('No fue posible calcular el valor total');
  });

  it('should formalize booking and navigate to payment when checkout is returned', async () => {
    await setup(RESERVATION_ID);
    spyOn(router, 'navigate').and.resolveTo(true);
    flushBooking();
    flushSummaryDependencies();
    completeGuestForm();

    component.createHold();

    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}/formalizar`);
    expect(req.request.body).toEqual({ intencion_pago: { monto: 820, moneda: 'COP' } });
    req.flush({
      mensaje: 'ok',
      pago: {
        id_pago: 'pay-1',
        id_reserva: RESERVATION_ID,
        referencia: 'PAY-1',
        estado: 'PENDING',
        monto: 820,
        moneda: 'COP',
        checkout: {
          public_key: 'pub',
          currency: 'COP',
          amount_in_cents: 82000,
          reference: 'PAY-1',
          signature_integrity: 'sig',
        },
      },
    });

    expect(sessionStorage.getItem(`travelhub.payment.${RESERVATION_ID}`)).toContain('PAY-1');
    expect(router.navigate).toHaveBeenCalledWith(['/booking', RESERVATION_ID, 'payment']);
  });

  it('should show controlled error when formalize response has no checkout', async () => {
    await setup(RESERVATION_ID);
    flushBooking();
    flushSummaryDependencies();
    completeGuestForm();

    component.createHold();

    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}/formalizar`);
    req.flush({ mensaje: 'formalizada' });

    expect(component.holdError()).toContain('backend no devol');
  });

  it('should navigate to rejected confirmation when formalize fails', async () => {
    await setup(RESERVATION_ID);
    spyOn(router, 'navigate').and.resolveTo(true);
    flushBooking();
    flushSummaryDependencies();
    completeGuestForm();

    component.createHold();

    const req = httpTesting.expectOne(`${environment.bookingApiUrl}/${RESERVATION_ID}/formalizar`);
    req.flush({ message: 'No hay disponibilidad' }, { status: 409, statusText: 'Conflict' });

    expect(component.holdError()).toBe('No hay disponibilidad');
    expect(router.navigate).toHaveBeenCalledWith(['/booking', RESERVATION_ID, 'confirm-reservation'], {
      queryParams: {
        status: 'rejected',
        reason: 'No hay disponibilidad',
      },
    });
  });

  it('should navigate back using category fallback when there is no browser history', async () => {
    await setup(RESERVATION_ID);
    spyOnProperty(window.history, 'length', 'get').and.returnValue(1);
    spyOn(router, 'navigate').and.resolveTo(true);
    flushBooking();
    flushSummaryDependencies();

    component.goBack();

    expect(router.navigate).toHaveBeenCalledWith(['/category', CATEGORY_ID], {
      queryParams: {
        fecha_inicio: '2026-05-01',
        fecha_fin: '2026-05-05',
        huespedes: 3,
      },
    });
  });

  it('should use browser history when available', async () => {
    await setup();
    spyOnProperty(window.history, 'length', 'get').and.returnValue(2);
    spyOn(location, 'back');

    component.goBack();

    expect(location.back).toHaveBeenCalled();
  });

  it('should navigate to results when no back context exists', async () => {
    await setup();
    spyOnProperty(window.history, 'length', 'get').and.returnValue(1);
    spyOn(router, 'navigate').and.resolveTo(true);

    component.goBack();

    expect(router.navigate).toHaveBeenCalledWith(['/resultados']);
  });
});
