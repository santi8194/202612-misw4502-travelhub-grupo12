import { Location } from '@angular/common';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { ActivatedRoute, convertToParamMap, provideRouter, Router } from '@angular/router';
import { of } from 'rxjs';
import {
  CancellationPreview,
  CancellationResult,
} from '../../models/reservation.interface';
import { CancelReservationTodoPage } from './cancel-reservation-todo-page';

const RESERVATION_ID = 'reserva-123';

function buildPreview(overrides: Partial<CancellationPreview> = {}): CancellationPreview {
  return {
    reservationId: RESERVATION_ID,
    reservationNumber: 'BKUTQOPB5C',
    hotelName: 'Hotel Central',
    location: 'Bogota, Colombia',
    checkInDate: '2026-06-10',
    checkOutDate: '2026-06-13',
    guests: 2,
    currentStatus: 'CONFIRMADA',
    totalPaid: 580,
    currency: 'USD',
    canCancel: true,
    nonCancelableReason: null,
    pmsStatus: 'CONFIRMED',
    mensaje: null,
    cancellationPolicy: {
      type: 'PARTIAL_REFUND',
      label: 'Reembolso parcial',
      description: 'Se aplica una penalidad del 50%.',
      diasAnticipacion: 3,
      porcentajePenalidad: 50,
    },
    refund: {
      paidAmount: 580,
      expectedRefundAmount: 290,
      refundStatus: 'PENDING',
      processingTimeLabel: '5 a 10 dias habiles',
    },
    ...overrides,
  };
}

function buildResult(overrides: Partial<CancellationResult> = {}): CancellationResult {
  return {
    reservationId: RESERVATION_ID,
    reservationStatus: 'CANCELACION_EN_PROCESO',
    cancellationReference: 'CXL-BK002',
    refundAmount: 290,
    refundStatus: 'PENDING',
    processingTimeLabel: '5 a 10 dias habiles',
    pmsStatus: 'PENDING',
    mensaje: 'La cancelacion espera confirmacion del PMS.',
    ...overrides,
  };
}

describe('CancelReservationTodoPage', () => {
  let fixture: ComponentFixture<CancelReservationTodoPage>;
  let httpMock: HttpTestingController;
  let locationSpy: jasmine.SpyObj<Location>;
  let router: Router;

  async function setup(routeId: string | null = RESERVATION_ID): Promise<void> {
    locationSpy = jasmine.createSpyObj<Location>('Location', ['back']);

    await TestBed.configureTestingModule({
      imports: [CancelReservationTodoPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Location, useValue: locationSpy },
        {
          provide: ActivatedRoute,
          useValue: {
            queryParams: of({}),
            snapshot: {
              paramMap: convertToParamMap(routeId ? { id_reserva: routeId } : {}),
            },
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CancelReservationTodoPage);
    httpMock = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);
    fixture.detectChanges();
  }

  afterEach(() => {
    httpMock?.verify();
  });

  it('reads id_reserva, requests the preview and shows loading while waiting', async () => {
    await setup();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-reservation-loading"]')).toBeTruthy();
    const request = httpMock.expectOne(req => req.url.includes(`/api/reserva/${RESERVATION_ID}/cancelacion-preview`));
    expect(request.request.method).toBe('GET');
    request.flush(buildPreview());
  });

  it('renders loaded summary, active policy and refund data', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-summary-hotel"]').textContent).toContain('Hotel Central');
    expect(fixture.nativeElement.querySelector('[data-testid="cancel-summary-location"]').textContent).toContain('Bogota, Colombia');
    expect(fixture.nativeElement.querySelector('[data-testid="cancel-refund-expected"]').textContent).toContain('290');
    expect(fixture.nativeElement.querySelector('[data-testid="cancel-refund-status"]').textContent).toContain('Pendiente');
    const activePolicy = fixture.nativeElement.querySelector('.policy-option--active');
    expect(activePolicy.textContent).toContain('Reembolso parcial');
  });

  it('renders friendly fallbacks for nullable preview fields', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview({
      hotelName: null,
      location: null,
      checkInDate: null,
      checkOutDate: null,
    }));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-summary-hotel"]').textContent).toContain('No disponible');
    expect(fixture.nativeElement.querySelector('[data-testid="cancel-summary-location"]').textContent).toContain('No disponible');
    expect(fixture.nativeElement.textContent).toContain('No disponible');
  });

  it('shows non cancelable reason and hides the cancel action', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview({
      canCancel: false,
      nonCancelableReason: 'La politica ya no permite cancelacion.',
    }));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-reservation-non-cancelable"]').textContent)
      .toContain('La politica ya no permite cancelacion.');
    expect(fixture.nativeElement.querySelector('[data-testid="cancel-open-warning"]')).toBeNull();
  });

  it('shows cancellation processing when the preview reports pending PMS', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview({
      currentStatus: 'CANCELACION_EN_PROCESO',
      pmsStatus: 'PENDING',
      mensaje: 'Esperando confirmacion PMS.',
    }));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-reservation-processing"]').textContent)
      .toContain('Esperando confirmacion PMS.');
  });

  [
    { status: 401, selector: 'cancel-reservation-unauthorized' },
    { status: 403, selector: 'cancel-reservation-unauthorized' },
    { status: 404, selector: 'cancel-reservation-not-found' },
    { status: 500, selector: 'cancel-reservation-error' },
  ].forEach(({ status, selector }) => {
    it(`handles preview ${status}`, async () => {
      await setup();
      httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush({}, { status, statusText: 'Error' });
      fixture.detectChanges();

      expect(fixture.nativeElement.querySelector(`[data-testid="${selector}"]`)).toBeTruthy();
    });
  });

  it('keeps optional reason text and navigates back when keeping the reservation', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();
    const navigateSpy = spyOn(router, 'navigate').and.resolveTo(true);
    const textarea = fixture.nativeElement.querySelector('[data-testid="cancel-reason"]') as HTMLTextAreaElement;
    textarea.value = 'Cambio de planes';
    textarea.dispatchEvent(new Event('input'));

    const keepButton = fixture.nativeElement.querySelector('[data-testid="cancel-keep-reservation"]') as HTMLButtonElement;
    keepButton.click();

    expect(textarea.value).toBe('Cambio de planes');
    expect(navigateSpy).toHaveBeenCalledWith(['/mis-reservas', RESERVATION_ID]);
  });

  it('opens warning before submit and requires accepted terms', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();

    (fixture.nativeElement.querySelector('[data-testid="cancel-open-warning"]') as HTMLButtonElement).click();
    fixture.detectChanges();

    const checkbox = fixture.nativeElement.querySelector('[data-testid="cancel-terms"]') as HTMLInputElement;
    const confirmButton = fixture.nativeElement.querySelector('[data-testid="cancel-confirm"]') as HTMLButtonElement;
    expect(checkbox.checked).toBeFalse();
    expect(confirmButton.disabled).toBeTrue();

    checkbox.checked = true;
    checkbox.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    expect(confirmButton.disabled).toBeFalse();
  });

  it('closes warning without calling backend', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();
    (fixture.nativeElement.querySelector('[data-testid="cancel-open-warning"]') as HTMLButtonElement).click();
    fixture.detectChanges();

    const closeButton = fixture.nativeElement.querySelector('[data-testid="cancel-close-warning"]') as HTMLButtonElement;
    closeButton.click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-warning-modal"]')).toBeNull();
    httpMock.expectNone(req => req.url.includes('/cancelar'));
  });

  it('submits once with accepted terms and a trimmed reason', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();
    const textarea = fixture.nativeElement.querySelector('[data-testid="cancel-reason"]') as HTMLTextAreaElement;
    textarea.value = '  Cambio de planes  ';
    textarea.dispatchEvent(new Event('input'));
    openAndAcceptTerms(fixture);

    const confirmButton = fixture.nativeElement.querySelector('[data-testid="cancel-confirm"]') as HTMLButtonElement;
    confirmButton.click();
    confirmButton.click();

    const request = httpMock.expectOne(req => req.url.includes(`/api/reserva/${RESERVATION_ID}/cancelar`));
    expect(request.request.body).toEqual({
      acceptedTerms: true,
      reason: 'Cambio de planes',
    });
    request.flush(buildResult());
  });

  it('omits blank reason and shows processing for CANCELACION_EN_PROCESO', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();
    const textarea = fixture.nativeElement.querySelector('[data-testid="cancel-reason"]') as HTMLTextAreaElement;
    textarea.value = '   ';
    textarea.dispatchEvent(new Event('input'));
    openAndAcceptTerms(fixture);
    (fixture.nativeElement.querySelector('[data-testid="cancel-confirm"]') as HTMLButtonElement).click();

    const request = httpMock.expectOne(req => req.url.includes('/cancelar'));
    expect(request.request.body).toEqual({ acceptedTerms: true });
    request.flush(buildResult());
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-reservation-processing"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('[data-testid="cancel-processing-reference"]').textContent).toContain('CXL-BK002');
  });

  it('shows success only when backend returns CANCELADA', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();
    openAndAcceptTerms(fixture);
    (fixture.nativeElement.querySelector('[data-testid="cancel-confirm"]') as HTMLButtonElement).click();
    httpMock.expectOne(req => req.url.includes('/cancelar')).flush(buildResult({
      reservationStatus: 'CANCELADA',
      pmsStatus: 'CONFIRMED',
    }));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-reservation-success"]')).toBeTruthy();
  });

  it('shows submit errors without showing success', async () => {
    await setup();
    httpMock.expectOne(req => req.url.includes('cancelacion-preview')).flush(buildPreview());
    fixture.detectChanges();
    openAndAcceptTerms(fixture);
    (fixture.nativeElement.querySelector('[data-testid="cancel-confirm"]') as HTMLButtonElement).click();
    httpMock.expectOne(req => req.url.includes('/cancelar')).flush(
      { mensaje: 'Estado invalido' },
      { status: 409, statusText: 'Conflict' }
    );
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[data-testid="cancel-submit-error"]').textContent).toContain('Estado invalido');
    expect(fixture.nativeElement.querySelector('[data-testid="cancel-reservation-success"]')).toBeNull();
  });
});

function openAndAcceptTerms(fixture: ComponentFixture<CancelReservationTodoPage>): void {
  (fixture.nativeElement.querySelector('[data-testid="cancel-open-warning"]') as HTMLButtonElement).click();
  fixture.detectChanges();
  const checkbox = fixture.nativeElement.querySelector('[data-testid="cancel-terms"]') as HTMLInputElement;
  checkbox.checked = true;
  checkbox.dispatchEvent(new Event('change'));
  fixture.detectChanges();
}
