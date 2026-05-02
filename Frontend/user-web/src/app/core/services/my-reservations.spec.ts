import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { MyReservationsService } from './my-reservations';
import { environment } from '../../../environments/environment';
import {
  BookingReservation,
  CalculateRoomPriceResponse,
  CategoryApiResponse,
  PaymentInfo,
} from '../../models/reservation.interface';

describe('MyReservationsService', () => {
  let httpTesting: HttpTestingController;

  const BOOKING_URL = environment.bookingApiUrl;
  const CATALOG_URL = environment.catalogApiUrl;
  const PAYMENT_URL = environment.paymentApiUrl;

  const MOCK_LOCALE = { pais: 'Colombia', id_usuario: 'cc912e74-927e-4166-802b-3ba6a3615ebf' };

  const MOCK_BOOKING: BookingReservation = {
    id_reserva: 'res-001',
    id_usuario: MOCK_LOCALE.id_usuario,
    id_categoria: 'cat-001',
    estado: 'CONFIRMADA',
    fecha_check_in: '2026-03-07',
    fecha_check_out: '2026-03-10',
    fecha_creacion: '2026-01-01T00:00:00',
    fecha_actualizacion: '2026-01-01T00:00:00',
    codigo_confirmacion_ota: 'TH-001',
    codigo_localizador_pms: '',
    ocupacion: { adultos: 2, ninos: 0, infantes: 0 },
  };

  const MOCK_BOOKING_HOLD: BookingReservation = {
    id_reserva: 'res-002',
    id_usuario: MOCK_LOCALE.id_usuario,
    id_categoria: 'cat-002',
    estado: 'HOLD',
    fecha_check_in: '2026-04-09',
    fecha_check_out: '2026-04-14',
    fecha_creacion: '2026-01-02T00:00:00',
    fecha_actualizacion: '2026-01-02T00:00:00',
    codigo_confirmacion_ota: '',
    codigo_localizador_pms: '',
    ocupacion: { adultos: 4, ninos: 0, infantes: 0 },
  };

  const MOCK_CATEGORY: CategoryApiResponse = {
    id_categoria: 'cat-001',
    nombre_comercial: 'Suite Deluxe',
    foto_portada_url: 'https://example.com/img.jpg',
  };

  const MOCK_CATEGORY_2: CategoryApiResponse = {
    id_categoria: 'cat-002',
    nombre_comercial: 'Coastal Bay Room',
    foto_portada_url: null,
  };

  const MOCK_APPROVED_PAYMENT: PaymentInfo = {
    id: 'pay-001',
    reservation_id: 'res-001',
    state: 'APPROVED',
    amount: 580,
    currency: 'USD',
  };

  const MOCK_REJECTED_PAYMENT: PaymentInfo = {
    id: 'pay-002',
    reservation_id: 'res-002',
    state: 'REJECTED',
    amount: 0,
    currency: 'USD',
  };

  const MOCK_PRICE: CalculateRoomPriceResponse = {
    total: 550.50,
    moneda: 'COP',
    noches: 5,
    precio_por_noche: 100.0,
    subtotal: 500.0,
    impuestos: 35.50,
    cargo_servicio: 15.0,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  function createService(): MyReservationsService {
    return TestBed.inject(MyReservationsService);
  }

  function flushLocale(): void {
    httpTesting.expectOne('assets/data/user-locale.json').flush(MOCK_LOCALE);
  }

  function flushBookings(bookings: BookingReservation[]): void {
    httpTesting
      .expectOne(`${BOOKING_URL}/usuario/${MOCK_LOCALE.id_usuario}`)
      .flush(bookings);
  }

  function flushEnrichApproved(booking: BookingReservation, category: CategoryApiResponse = MOCK_CATEGORY): void {
    httpTesting.expectOne(`${CATALOG_URL}/categories/${booking.id_categoria}`).flush(category);
    httpTesting.expectOne(`${PAYMENT_URL}/payments/by-reserva/${booking.id_reserva}`)
      .flush([MOCK_APPROVED_PAYMENT]);
  }

  function flushEnrichNoApproved(
    booking: BookingReservation,
    payments: PaymentInfo[],
    category: CategoryApiResponse,
    price: CalculateRoomPriceResponse = MOCK_PRICE
  ): void {
    httpTesting.expectOne(`${CATALOG_URL}/categories/${booking.id_categoria}`).flush(category);
    httpTesting.expectOne(`${PAYMENT_URL}/payments/by-reserva/${booking.id_reserva}`)
      .flush(payments);
    httpTesting
      .expectOne(req => req.method === 'POST' && req.url === `${CATALOG_URL}/calculate-room-price`)
      .flush(price);
  }

  it('should be created', () => {
    const service = createService();
    expect(service).toBeTruthy();
    flushLocale();
    flushBookings([MOCK_BOOKING]);
    flushEnrichApproved(MOCK_BOOKING);
  });

  it('should fetch reservations from booking API using id_usuario from locale', () => {
    createService();
    flushLocale();
    const bookingReq = httpTesting.expectOne(
      `${BOOKING_URL}/usuario/${MOCK_LOCALE.id_usuario}`
    );
    expect(bookingReq.request.method).toBe('GET');
    bookingReq.flush([MOCK_BOOKING]);
    flushEnrichApproved(MOCK_BOOKING);
  });

  it('should fetch category info for each reservation', () => {
    createService();
    flushLocale();
    flushBookings([MOCK_BOOKING]);
    const catReq = httpTesting.expectOne(`${CATALOG_URL}/categories/${MOCK_BOOKING.id_categoria}`);
    expect(catReq.request.method).toBe('GET');
    catReq.flush(MOCK_CATEGORY);
    httpTesting.expectOne(`${PAYMENT_URL}/payments/by-reserva/${MOCK_BOOKING.id_reserva}`)
      .flush([MOCK_APPROVED_PAYMENT]);
  });

  it('should fetch payments for each reservation', () => {
    createService();
    flushLocale();
    flushBookings([MOCK_BOOKING]);
    httpTesting.expectOne(`${CATALOG_URL}/categories/${MOCK_BOOKING.id_categoria}`).flush(MOCK_CATEGORY);
    const payReq = httpTesting.expectOne(`${PAYMENT_URL}/payments/by-reserva/${MOCK_BOOKING.id_reserva}`);
    expect(payReq.request.method).toBe('GET');
    payReq.flush([MOCK_APPROVED_PAYMENT]);
  });

  it('should use payment.amount and payment.currency when APPROVED payment exists', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING]);
    flushEnrichApproved(MOCK_BOOKING);

    const vm = service.reservations()[0];
    expect(vm.monto_total).toBe(MOCK_APPROVED_PAYMENT.amount);
    expect(vm.moneda).toBe(MOCK_APPROVED_PAYMENT.currency);
  });

  it('should call POST calculate-room-price when no APPROVED payment exists', () => {
    createService();
    flushLocale();
    flushBookings([MOCK_BOOKING_HOLD]);
    httpTesting.expectOne(`${CATALOG_URL}/categories/${MOCK_BOOKING_HOLD.id_categoria}`).flush(MOCK_CATEGORY_2);
    httpTesting.expectOne(`${PAYMENT_URL}/payments/by-reserva/${MOCK_BOOKING_HOLD.id_reserva}`).flush([]);
    const priceReq = httpTesting.expectOne(
      req => req.method === 'POST' && req.url === `${CATALOG_URL}/calculate-room-price`
    );
    expect(priceReq.request.body).toEqual({
      id_categoria: MOCK_BOOKING_HOLD.id_categoria,
      fecha_inicio: MOCK_BOOKING_HOLD.fecha_check_in,
      fecha_fin: MOCK_BOOKING_HOLD.fecha_check_out,
      pais_usuario: MOCK_LOCALE.pais,
    });
    priceReq.flush(MOCK_PRICE);
  });

  it('should use calculate-room-price total and moneda as fallback when no APPROVED payment', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING_HOLD]);
    flushEnrichNoApproved(MOCK_BOOKING_HOLD, [], MOCK_CATEGORY_2);

    const vm = service.reservations()[0];
    expect(vm.monto_total).toBe(MOCK_PRICE.total);
    expect(vm.moneda).toBe(MOCK_PRICE.moneda);
  });

  it('should handle 404 from payment gracefully and fall back to calculate-room-price', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING_HOLD]);
    httpTesting.expectOne(`${CATALOG_URL}/categories/${MOCK_BOOKING_HOLD.id_categoria}`).flush(MOCK_CATEGORY_2);
    httpTesting.expectOne(`${PAYMENT_URL}/payments/by-reserva/${MOCK_BOOKING_HOLD.id_reserva}`)
      .flush(null, { status: 404, statusText: 'Not Found' });
    httpTesting
      .expectOne(req => req.method === 'POST' && req.url === `${CATALOG_URL}/calculate-room-price`)
      .flush(MOCK_PRICE);

    const vm = service.reservations()[0];
    expect(vm.estado).toBe('PENDIENTE_PAGO');
  });

  it('should resolve PENDIENTE_PAGO when payment state is REJECTED', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING_HOLD]);
    flushEnrichNoApproved(MOCK_BOOKING_HOLD, [MOCK_REJECTED_PAYMENT], MOCK_CATEGORY_2);

    const vm = service.reservations()[0];
    expect(vm.estado).toBe('PENDIENTE_PAGO');
  });

  it('should map booking + category + payment fields correctly to ReservationViewModel', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING]);
    flushEnrichApproved(MOCK_BOOKING);

    const vm = service.reservations()[0];
    expect(vm.id_reserva).toBe(MOCK_BOOKING.id_reserva);
    expect(vm.nombre_comercial).toBe(MOCK_CATEGORY.nombre_comercial);
    expect(vm.foto_portada_url).toBe(MOCK_CATEGORY.foto_portada_url);
    expect(vm.estado).toBe('CONFIRMADA');
    expect(vm.fecha_check_in).toBe(MOCK_BOOKING.fecha_check_in);
    expect(vm.fecha_check_out).toBe(MOCK_BOOKING.fecha_check_out);
    expect(vm.total_huespedes).toBe(2);
    expect(vm.codigo_confirmacion).toBe('TH-001');
  });

  it('should select APPROVED payment when multiple payments with different states exist', () => {
    const pendingPayment: PaymentInfo = { ...MOCK_APPROVED_PAYMENT, id: 'pay-old', state: 'PENDING' };
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING]);
    httpTesting.expectOne(`${CATALOG_URL}/categories/${MOCK_BOOKING.id_categoria}`).flush(MOCK_CATEGORY);
    httpTesting.expectOne(`${PAYMENT_URL}/payments/by-reserva/${MOCK_BOOKING.id_reserva}`)
      .flush([pendingPayment, MOCK_APPROVED_PAYMENT]);

    const vm = service.reservations()[0];
    expect(vm.monto_total).toBe(MOCK_APPROVED_PAYMENT.amount);
    expect(vm.moneda).toBe(MOCK_APPROVED_PAYMENT.currency);
    expect(vm.estado).toBe('CONFIRMADA');
  });

  it('should compute counters correctly from loaded data', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING, MOCK_BOOKING_HOLD]);
    flushEnrichApproved(MOCK_BOOKING);
    flushEnrichNoApproved(MOCK_BOOKING_HOLD, [], MOCK_CATEGORY_2);

    const counters = service.counters();
    expect(counters.total).toBe(2);
    expect(counters.confirmadas).toBe(1);
    expect(counters.pendientes).toBe(1);
    expect(counters.canceladas).toBe(0);
  });

  it('should filter to only CONFIRMADA reservations', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING, MOCK_BOOKING_HOLD]);
    flushEnrichApproved(MOCK_BOOKING);
    flushEnrichNoApproved(MOCK_BOOKING_HOLD, [], MOCK_CATEGORY_2);

    service.setFilter('CONFIRMADA');
    const filtered = service.filteredReservations();
    expect(filtered.length).toBe(1);
    expect(filtered[0].estado).toBe('CONFIRMADA');
  });

  it('should filter to only PENDIENTE reservations', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING, MOCK_BOOKING_HOLD]);
    flushEnrichApproved(MOCK_BOOKING);
    flushEnrichNoApproved(MOCK_BOOKING_HOLD, [], MOCK_CATEGORY_2);

    service.setFilter('PENDIENTE');
    const filtered = service.filteredReservations();
    expect(filtered.length).toBe(1);
    expect(['PENDIENTE_PAGO', 'PENDIENTE_CONFIRMACION_HOTEL']).toContain(filtered[0].estado);
  });

  it('should return all reservations when filter is TODAS', () => {
    const service = createService();
    flushLocale();
    flushBookings([MOCK_BOOKING, MOCK_BOOKING_HOLD]);
    flushEnrichApproved(MOCK_BOOKING);
    flushEnrichNoApproved(MOCK_BOOKING_HOLD, [], MOCK_CATEGORY_2);

    service.setFilter('TODAS');
    expect(service.filteredReservations().length).toBe(2);
  });

  it('should return empty array when booking API fails', () => {
    const service = createService();
    flushLocale();
    httpTesting
      .expectOne(`${BOOKING_URL}/usuario/${MOCK_LOCALE.id_usuario}`)
      .flush(null, { status: 500, statusText: 'Internal Server Error' });

    expect(service.reservations()).toEqual([]);
  });

  it('should return empty array when booking list is empty', () => {
    const service = createService();
    flushLocale();
    flushBookings([]);

    expect(service.reservations()).toEqual([]);
  });
});
