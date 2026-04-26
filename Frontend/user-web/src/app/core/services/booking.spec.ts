import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { HttpErrorResponse } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { BookingService } from './booking';
import { HoldRequest } from '../../models/hold.interface';

describe('BookingService', () => {
  let service: BookingService;
  let httpTesting: HttpTestingController;

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
  });

  afterEach(() => httpTesting.verify());

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

    const req = httpTesting.expectOne('http://localhost:5001/booking/api/reserva');
    expect(req.request.method).toBe('POST');
    expect(req.request.body.id_categoria).toBe('1');
    expect(req.request.body.fecha_check_in).toBe('2026-10-10');
    expect(req.request.body.fecha_check_out).toBe('2026-10-15');
    expect(req.request.body.ocupacion).toEqual({ adultos: 2, ninos: 0, infantes: 0 });
    expect(req.request.body.id_usuario).toEqual(jasmine.any(String));
    req.flush({ id_reserva: 'reserva-123' });
  });

  it('should send a POST request to formalize a reservation', () => {
    service.formalizeBookingById('reserva-123').subscribe((response) => {
      expect(response).toEqual({
        mensaje: 'Reserva formalizada. Iniciando SAGA de confirmación con Hoteles y Pagos',
      });
    });

    const req = httpTesting.expectOne('http://localhost:5001/booking/api/reserva/reserva-123/formalizar');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({});
    req.flush({ mensaje: 'Reserva formalizada. Iniciando SAGA de confirmación con Hoteles y Pagos' });
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
      error: { mensaje: 'La tarifa configurada para la reserva ya no está vigente.' },
    });

    expect(service.getReservationErrorMessage(error)).toBe(
      'La tarifa configurada para la reserva ya no está vigente.'
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

    const req = httpTesting.expectOne('http://localhost:5001/booking/api/reserva');
    req.flush({ mensaje: 'No existe inventario para la categoria en la fecha 2026-04-12' });
  });
});
