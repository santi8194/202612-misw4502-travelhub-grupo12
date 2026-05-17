import { Component, provideZonelessChangeDetection } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter, Router, RouterLink } from '@angular/router';
import { Observable, of, throwError } from 'rxjs';
import { ProcessingReservationPage } from './processing-reservation-page';
import { BookingService } from '../../core/services/booking';
import { I18nService } from '../../core/i18n/i18n.service';
import { TranslatePipe } from '../../shared/pipes/translate.pipe';

@Component({
  selector: 'app-header',
  standalone: true,
  template: '',
})
class HeaderStubComponent {}

@Component({
  selector: 'app-footer',
  standalone: true,
  template: '',
})
class FooterStubComponent {}

@Component({
  standalone: true,
  template: '',
})
class ConfirmReservationRouteStubComponent {}

const reservationId = 'reserva-test-123';

describe('ProcessingReservationPage', () => {
  let fixture: ComponentFixture<ProcessingReservationPage>;
  let component: ProcessingReservationPage;
  let router: Router;

  async function setup(options: {
    status?: string;
    reason?: string;
    reservationId?: string | null;
    booking$?: Observable<any>;
  }): Promise<void> {
    const status = options.status ?? 'CONFIRMADA';
    const reason = options.reason;
    const idFromRoute = options.reservationId === undefined ? reservationId : options.reservationId;
    const booking$ = options.booking$ ?? of({ estado: status, motivo: reason });

    TestBed.resetTestingModule();

    await TestBed.configureTestingModule({
      imports: [ProcessingReservationPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([
          {
            path: 'booking/:id_reserva/confirm-reservation',
            component: ConfirmReservationRouteStubComponent,
          },
        ]),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: convertToParamMap(idFromRoute ? { id_reserva: idFromRoute } : {}),
              queryParamMap: convertToParamMap(reason ? { reason } : {}),
            },
          },
        },
        {
          provide: BookingService,
          useValue: {
            getBookingById: () => booking$,
          },
        },
        I18nService,
      ],
    })
      .overrideComponent(ProcessingReservationPage, {
        set: {
          imports: [RouterLink, TranslatePipe, HeaderStubComponent, FooterStubComponent],
        },
      })
      .compileComponents();

    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.resolveTo(true);

    fixture = TestBed.createComponent(ProcessingReservationPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  afterEach(() => {
    fixture?.destroy();
  });

  it('shows the return-to-cart action only when the reservation is confirmed', async () => {
    await setup({ status: 'CONFIRMADA' });

    const action = fixture.nativeElement.querySelector('.processing-action');

    expect(component.status()).toBe('CONFIRMADA');
    expect(action).not.toBeNull();
    expect(action.textContent).toContain('Volver al carrito');
  });

  it('hides the return-to-cart action when the reservation is cancelled', async () => {
    await setup({ status: 'CANCELADA', reason: 'La reserva fue cancelada' });

    const action = fixture.nativeElement.querySelector('.processing-action');

    expect(component.status()).toBe('CANCELADA');
    expect(action).toBeNull();
  });

  it('sets translated error when reservation id is missing in route', async () => {
    await setup({ reservationId: null });

    expect(component.isPolling()).toBeFalse();
    expect(component.pollingError()).toBe('No se encontró el identificador de reserva para consultar el estado.');
  });

  it('maps empty cancellation reason to the translated fallback reason', async () => {
    await setup({ status: 'CANCELADA', reason: '   ' });
    await fixture.whenStable();

    const navigateSpy = TestBed.inject(Router).navigate as jasmine.Spy;
    const i18n = TestBed.inject(I18nService);
    const lastCall = navigateSpy.calls.mostRecent();

    expect(lastCall).toBeDefined();
    expect(lastCall.args[1].queryParams.reason).toBe(i18n.translate('processing.rejectedReason'));
  });

  it('maps saga cancellation text to the saga-processing helper message', async () => {
    await setup({
      status: 'CANCELADA',
      reason: 'Cancelada durante el procesamiento de la saga',
    });
    await fixture.whenStable();

    const navigateSpy = TestBed.inject(Router).navigate as jasmine.Spy;
    const i18n = TestBed.inject(I18nService);
    const lastCall = navigateSpy.calls.mostRecent();

    expect(lastCall).toBeDefined();
    expect(lastCall.args[1].queryParams.reason).toBe(i18n.translate('processing.sagaProcessing'));
  });

  it('uses saga translation for initial reason when it mentions starting saga', async () => {
    await setup({
      status: 'PENDIENTE',
      reason: 'Iniciando SAGA de confirmación',
    });

    expect(component.message()).toBe('Tu reserva fue formalizada. Estamos confirmando la disponibilidad y el pago.');
  });

  it('sets retrying polling error when booking status request fails', async () => {
    await setup({
      booking$: throwError(() => new Error('network error')),
    });

    expect(component.pollingError()).toBe('No pudimos consultar el estado de la reserva. Reintentando...');
  });

  it('does not navigate twice after the reservation has already resolved', async () => {
    await setup({ status: 'CONFIRMADA' });

    const navigateSpy = TestBed.inject(Router).navigate as jasmine.Spy;
    const callsAfterFirstResolution = navigateSpy.calls.count();

    (component as any).resolveAndNavigate('confirmed', 'any reason');

    expect(navigateSpy.calls.count()).toBe(callsAfterFirstResolution);
  });

  it('returns translated saga rejection reason when cancellation marker is preserved', async () => {
    await setup({ status: 'PENDIENTE' });

    const i18n = TestBed.inject(I18nService);
    spyOn(component as any, 'sanitizeUserMessage').and.callFake((msg: string) => msg);

    const resolved = (component as any).buildCancellationReason('Cancelada durante el procesamiento de la saga');

    expect(resolved).toBe(i18n.translate('processing.rejectedSaga'));
  });

  it('returns early from pollStatus when a request is already in flight', async () => {
    await setup({ status: 'PENDIENTE' });

    const bookingService = TestBed.inject(BookingService);
    const getBookingSpy = spyOn(bookingService, 'getBookingById').and.callThrough();
    (component as any).isRequestInFlight = true;

    (component as any).pollStatus();

    expect(getBookingSpy).not.toHaveBeenCalled();
  });

  it('returns early from pollStatus after the page has already resolved', async () => {
    await setup({ status: 'CONFIRMADA' });

    const bookingService = TestBed.inject(BookingService);
    const getBookingSpy = spyOn(bookingService, 'getBookingById').and.callThrough();
    (component as any).hasResolved = true;

    (component as any).pollStatus();

    expect(getBookingSpy).not.toHaveBeenCalled();
  });

  it('keeps user messages untouched when they are not saga-related', async () => {
    await setup({ status: 'PENDIENTE' });

    const result = (component as any).sanitizeUserMessage('Mensaje de validación normal');

    expect(result).toBe('Mensaje de validación normal');
  });

  it('falls back to empty normalized status when response has no status field', async () => {
    await setup({ status: 'PENDIENTE' });

    component.pollingError.set('temp');
    (component as any).handleStatusResponse({});

    expect(component.status()).toBe('PENDIENTE');
    expect(component.pollingError()).toBeNull();
  });

  it('uses mensaje as cancellation reason when motivo is missing', async () => {
    await setup({ status: 'PENDIENTE' });

    (component as any).handleStatusResponse({ estado: 'CANCELADA', mensaje: 'Motivo desde mensaje' });

    const navigateSpy = TestBed.inject(Router).navigate as jasmine.Spy;
    const lastCall = navigateSpy.calls.mostRecent();
    expect(lastCall.args[1].queryParams.reason).toBe('Motivo desde mensaje');
  });

  it('uses detail as cancellation reason when motivo and mensaje are missing', async () => {
    await setup({ status: 'PENDIENTE' });

    (component as any).handleStatusResponse({ estado: 'CANCELADA', detail: 'Motivo desde detail' });

    const navigateSpy = TestBed.inject(Router).navigate as jasmine.Spy;
    const lastCall = navigateSpy.calls.mostRecent();
    expect(lastCall.args[1].queryParams.reason).toBe('Motivo desde detail');
  });

  it('uses error as cancellation reason when motivo, mensaje and detail are missing', async () => {
    await setup({ status: 'PENDIENTE' });

    (component as any).handleStatusResponse({ estado: 'CANCELADA', error: 'Motivo desde error' });

    const navigateSpy = TestBed.inject(Router).navigate as jasmine.Spy;
    const lastCall = navigateSpy.calls.mostRecent();
    expect(lastCall.args[1].queryParams.reason).toBe('Motivo desde error');
  });

  it('uses translated cancelled message when cancellation response has no reason fields', async () => {
    await setup({ status: 'PENDIENTE' });

    const i18n = TestBed.inject(I18nService);
    (component as any).handleStatusResponse({ estado: 'CANCELADA' });

    const navigateSpy = TestBed.inject(Router).navigate as jasmine.Spy;
    const lastCall = navigateSpy.calls.mostRecent();
    expect(lastCall.args[1].queryParams.reason).toBe(i18n.translate('processing.cancelled'));
  });
});
