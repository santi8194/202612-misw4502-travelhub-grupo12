import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { environment } from '../../../environments/environment';
import {
  ReservationEmailNotificationService,
  ReservationStatusEmailPayload,
} from './reservation-email-notification';

describe('ReservationEmailNotificationService', () => {
  let service: ReservationEmailNotificationService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(ReservationEmailNotificationService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should post reservation status email payload to notification endpoint', () => {
    const payload: ReservationStatusEmailPayload = {
      id_reserva: 'reserva-001',
      email_cliente: 'viajero@travelhub.com',
      estado: 'CONFIRMADA',
      codigo_reserva: 'ABC123',
    };

    service.sendReservationStatusEmail(payload).subscribe((response) => {
      expect(response).toEqual({ ok: true });
    });

    const req = httpTesting.expectOne(
      `${environment.notificationApiUrl}/notifications/reservations/status-email`
    );
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush({ ok: true });
  });
});
