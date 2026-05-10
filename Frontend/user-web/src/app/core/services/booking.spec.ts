import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { BookingService } from './booking';
import { HoldRequest } from '../../models/hold.interface';
import { environment } from '../../../environments/environment';

const BOOKING_URL = environment.bookingApiUrl;

describe('BookingService', () => {
  let service: BookingService;
  let httpTesting: HttpTestingController;
  const bookingApiUrl = environment.bookingApiUrl;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting()
      ],
    });
    service = TestBed.inject(BookingService);
    httpTesting = TestBed.inject(HttpTestingController);

    localStorage.setItem('th_access_token', 'acc-token-xyz');
    localStorage.setItem('th_refresh_token', 'ref-token-xyz');
    localStorage.setItem('th_token_type', 'Bearer');
    localStorage.setItem('th_user_email', 'juan@ejemplo.com');
    localStorage.setItem('th_user_id', 'test-user-uuid-001');
  });

  afterEach(() => {
    httpTesting.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should send a POST request to create a hold using the booking API contract', () => {
    const request: HoldRequest = {
      categoryId: 1,
      checkIn: '2026-10-10',
      checkOut: '2026-10-15',
      guests: 2
    };

    service.createHold(request).subscribe(response => {
      expect(response).toEqual({
        id: 'reserva-123',
        expiresAt: 0,
      });
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body.id_categoria).toBe('1');
    expect(req.request.body.fecha_check_in).toBe('2026-10-10');
    expect(req.request.body.fecha_check_out).toBe('2026-10-15');
    expect(req.request.body.ocupacion).toEqual({ adultos: 2, ninos: 0, infantes: 0 });
    expect(req.request.body.id_usuario).toBe('test-user-uuid-001');
    req.flush({ id_reserva: 'reserva-123' });
  });

  it('should send a POST request to formalize a reservation', () => {
    service.formalizeBookingById('reserva-123').subscribe((response) => {
      expect(response).toEqual({
        mensaje: 'Reserva formalizada. Iniciando SAGA de confirmacion con Hoteles y Pagos',
      });
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}/reserva-123/formalizar`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({});
    req.flush({ mensaje: 'Reserva formalizada. Iniciando SAGA de confirmacion con Hoteles y Pagos' });
  });

  it('should send payment intention when formalizing a reservation', () => {
    service.formalizeBookingById('reserva-123', {
      intencion_pago: {
        monto: 120000,
        moneda: 'COP',
      },
    }).subscribe((response) => {
      expect(response.pago?.checkout?.reference).toBe('PAY-1');
    });

    const req = httpTesting.expectOne(`${bookingApiUrl}/reserva-123/formalizar`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      intencion_pago: {
        monto: 120000,
        moneda: 'COP',
      },
    });
    req.flush({
      mensaje: 'Reserva formalizada. Iniciando SAGA de confirmacion con Hoteles y Pagos',
      pago: {
        id_pago: 'pay-1',
        id_reserva: 'reserva-123',
        referencia: 'PAY-1',
        estado: 'PENDING',
        monto: 120000,
        moneda: 'COP',
        checkout: {
          public_key: 'pub_test',
          currency: 'COP',
          amount_in_cents: 12000000,
          reference: 'PAY-1',
          signature_integrity: 'sig',
        },
      },
    });
  });

  it('should describe availability errors clearly', () => {
    const error = new HttpErrorResponse({
      status: 409,
      error: { message: 'No hay disponibilidad para las fechas seleccionadas' },
    });

    expect(service.getReservationErrorMessage(error)).toBe(
      'No hay disponibilidad para las fechas seleccionadas'
    );
  });

  it('should keep a specific backend message when it is already useful', () => {
    const error = new HttpErrorResponse({
      status: 400,
      error: { mensaje: 'La tarifa configurada para la reserva ya no esta vigente.' },
    });

    expect(service.getReservationErrorMessage(error)).toBe(
      'La tarifa configurada para la reserva ya no esta vigente.'
    );
  });

  it('should fail createBooking with the backend business message when id_reserva is missing', () => {
    const request = {
      id_usuario: 'user-1',
      id_categoria: 'cat-1',
      fecha_check_in: '2026-04-12',
      fecha_check_out: '2026-04-13',
      ocupacion: {
        adultos: 2,
        ninos: 0,
        infantes: 0,
      },
    };

    service.createBooking(request).subscribe({
      next: () => fail('Expected createBooking to fail when id_reserva is missing'),
      error: (error: Error) => {
        expect(service.getReservationErrorMessage(error)).toBe(
          'No existe inventario para la categoria en la fecha 2026-04-12'
        );
      },
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}`);
    req.flush({ mensaje: 'No existe inventario para la categoria en la fecha 2026-04-12' });
  });

  it('should fail createHold when user session is missing', () => {
    localStorage.clear();
    const request: HoldRequest = {
      categoryId: 'cat-1',
      checkIn: '2026-10-10',
      checkOut: '2026-10-15',
      guests: 2,
    };

    service.createHold(request).subscribe({
      next: () => fail('Expected createHold to fail without user session'),
      error: (error: Error) => {
        expect(error.message).toContain('Inicia sesi');
      },
    });

    httpTesting.expectNone(`${BOOKING_URL}`);
  });

  it('should read booking by id', () => {
    service.getBookingById('reserva-123').subscribe((response) => {
      expect(response.id_reserva).toBe('reserva-123');
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}/reserva-123`);
    expect(req.request.method).toBe('GET');
    req.flush({ id_reserva: 'reserva-123' });
  });

  it('should propagate booking read errors', () => {
    service.getBookingById('reserva-123').subscribe({
      next: () => fail('Expected getBookingById to fail'),
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(500);
      },
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}/reserva-123`);
    req.flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
  });

  it('should expire booking by id', () => {
    service.expireBookingById('reserva-123').subscribe((response) => {
      expect(response.estado).toBe('EXPIRADA');
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}/reserva-123/expirar`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({});
    req.flush({ estado: 'EXPIRADA' });
  });

  it('should propagate expire booking errors', () => {
    service.expireBookingById('reserva-123').subscribe({
      next: () => fail('Expected expireBookingById to fail'),
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(409);
      },
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}/reserva-123/expirar`);
    req.flush({ message: 'No expirable' }, { status: 409, statusText: 'Conflict' });
  });

  it('should read catalog, category and categories endpoints', () => {
    service.getCatalogByCategoryId('cat-1').subscribe((response) => {
      expect(response.id_categoria).toBe('cat-1');
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/cat-1`)
      .flush({ id_categoria: 'cat-1' });

    service.getCategoryById('cat-1').subscribe((response) => {
      expect(response.nombre_comercial).toBe('Suite');
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/cat-1`)
      .flush({ nombre_comercial: 'Suite' });

    service.getPropertyCategories('prop-1').subscribe((response) => {
      expect(response.length).toBe(1);
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/prop-1/categories`)
      .flush([{ id_categoria: 'cat-1' }]);
  });

  it('should fallback when primary property endpoint fails', () => {
    service.getPropertyById('prop-1').subscribe((response) => {
      expect(response.nombre).toBe('Hotel fallback');
    });

    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/prop-1`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/property/prop-1`)
      .flush({ nombre: 'Hotel fallback' });
  });

  it('should propagate property fallback errors', () => {
    service.getPropertyById('prop-1').subscribe({
      next: () => fail('Expected getPropertyById to fail'),
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(404);
      },
    });

    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/prop-1`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
    httpTesting.expectOne(`${environment.catalogApiUrl}/property/prop-1`)
      .flush({ error: 'missing' }, { status: 404, statusText: 'Not Found' });
  });

  it('should propagate catalog endpoint errors', () => {
    service.getCatalogByCategoryId('cat-1').subscribe({
      next: () => fail('Expected getCatalogByCategoryId to fail'),
      error: (error: HttpErrorResponse) => expect(error.status).toBe(500),
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/by-category/cat-1`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });

    service.getCategoryById('cat-1').subscribe({
      next: () => fail('Expected getCategoryById to fail'),
      error: (error: HttpErrorResponse) => expect(error.status).toBe(500),
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/categories/cat-1`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });

    service.getPropertyCategories('prop-1').subscribe({
      next: () => fail('Expected getPropertyCategories to fail'),
      error: (error: HttpErrorResponse) => expect(error.status).toBe(500),
    });
    httpTesting.expectOne(`${environment.catalogApiUrl}/properties/prop-1/categories`)
      .flush({ error: 'fail' }, { status: 500, statusText: 'Server Error' });
  });

  it('should create booking when backend returns reservation id', () => {
    const request = {
      id_usuario: 'user-1',
      id_categoria: 'cat-1',
      fecha_check_in: '2026-04-12',
      fecha_check_out: '2026-04-13',
      ocupacion: {
        adultos: 2,
        ninos: 0,
        infantes: 0,
      },
    };

    service.createBooking(request).subscribe((response) => {
      expect(response.id_reserva).toBe('reserva-123');
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}`);
    expect(req.request.method).toBe('POST');
    req.flush({ id_reserva: 'reserva-123' });
  });

  it('should fail createBooking with generic message when id_reserva and message are missing', () => {
    const request = {
      id_usuario: 'user-1',
      id_categoria: 'cat-1',
      fecha_check_in: '2026-04-12',
      fecha_check_out: '2026-04-13',
      ocupacion: {
        adultos: 2,
        ninos: 0,
        infantes: 0,
      },
    };

    service.createBooking(request).subscribe({
      next: () => fail('Expected createBooking to fail'),
      error: (error: Error) => {
        expect(error.message).toContain('identificador');
      },
    });

    const req = httpTesting.expectOne(`${BOOKING_URL}`);
    req.flush({});
  });

  it('should map generic transport and backend errors to useful reservation messages', () => {
    expect(service.getReservationErrorMessage(new HttpErrorResponse({ status: 0 }))).toContain('comunicarse');
    expect(service.getReservationErrorMessage(new HttpErrorResponse({ status: 404 }))).toContain('No fue posible crear');
    expect(service.getReservationErrorMessage(new HttpErrorResponse({ status: 409 }))).toContain('disponibilidad');
    expect(service.getReservationErrorMessage(new HttpErrorResponse({ status: 422, error: { message: 'Bad request' } }))).toContain('datos enviados');
    expect(service.getReservationErrorMessage(new HttpErrorResponse({ status: 400, error: { message: 'Bad request' } }))).toContain('No hay disponibilidad');
    expect(service.getReservationErrorMessage(new HttpErrorResponse({ status: 500, error: { message: 'Internal server error' } }))).toContain('present');
  });

  it('should extract nested backend messages and fallback when message is generic or absent', () => {
    const nestedError = new HttpErrorResponse({
      status: 400,
      error: {
        errors: [
          { detail: '' },
          { title: 'La categoria no encontrada' },
        ],
      },
    });
    expect(service.getReservationErrorMessage(nestedError)).toBe('La categoria no encontrada');

    expect(service.getReservationErrorMessage('   fechas invalidas   ')).toContain('fechas invalidas');
    expect(service.getReservationErrorMessage(new Error('ocupacion invalida'))).toContain('ocupacion invalida');
    expect(service.getReservationErrorMessage({}, 'Mensaje fallback')).toBe('Mensaje fallback');
  });
});
