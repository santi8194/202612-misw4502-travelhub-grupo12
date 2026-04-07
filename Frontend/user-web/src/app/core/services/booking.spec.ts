import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { BookingService } from './booking';
import { HoldRequest, HoldResponse } from '../../models/hold.interface';

describe('BookingService', () => {
  let service: BookingService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(BookingService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should send a POST request to create a hold', () => {
    const request: HoldRequest = {
      categoryId: 1,
      checkIn: '2026-10-10',
      checkOut: '2026-10-15',
      guests: 2
    };

    const mockResponse: HoldResponse = {
      id: 'hold-123',
      expiresAt: Date.now() + 15 * 60 * 1000
    };

    service.createHold(request).subscribe(response => {
      expect(response.id).toBe('hold-123');
      expect(response.expiresAt).toBeDefined();
    });

    const req = httpTesting.expectOne(req => req.url.endsWith('/bookings/hold'));
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(request);
    req.flush(mockResponse);
  });
});
