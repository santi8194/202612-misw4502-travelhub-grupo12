import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { PaymentPage } from './payment-page';
import { PAYMENT_STORAGE_PREFIX } from '../../core/storage/payment-storage';

describe('PaymentPage', () => {
  let fixture: ComponentFixture<PaymentPage>;
  let widgetConfig: unknown;
  let widgetOpenSpy: jasmine.Spy;

  const routeStub = {
    snapshot: {
      paramMap: convertToParamMap({ id_reserva: 'reserva-123' }),
    },
  };

  beforeEach(async () => {
    sessionStorage.clear();
    widgetConfig = null;
    widgetOpenSpy = jasmine.createSpy('open');
    (window as any).WidgetCheckout = function (config: unknown) {
      widgetConfig = config;
      return {
        open: widgetOpenSpy,
      };
    };

    await TestBed.configureTestingModule({
      imports: [PaymentPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        { provide: ActivatedRoute, useValue: routeStub },
      ],
    }).compileComponents();
  });

  afterEach(() => {
    sessionStorage.clear();
    delete (window as any).WidgetCheckout;
  });

  it('should show an error when payment intent is missing', () => {
    fixture = TestBed.createComponent(PaymentPage);
    fixture.detectChanges();

    const error = fixture.nativeElement.querySelector('[data-testid="payment-error"]');
    expect(error).toBeTruthy();
    expect(error.textContent).toContain('No se encontro una intencion de pago activa');
  });

  it('should configure Wompi checkout with required fields', async () => {
    sessionStorage.setItem(
      `${PAYMENT_STORAGE_PREFIX}reserva-123`,
      JSON.stringify({
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
      })
    );

    fixture = TestBed.createComponent(PaymentPage);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('[data-testid="wompi-open-button"]');
    expect(button).toBeTruthy();
    expect(button.disabled).toBeFalse();

    button.click();

    expect(widgetOpenSpy).toHaveBeenCalled();
    expect(widgetConfig).toEqual(jasmine.objectContaining({
      publicKey: 'pub_test',
      currency: 'COP',
      amountInCents: 12000000,
      reference: 'PAY-1',
      signature: { integrity: 'sig' },
      redirectUrl: jasmine.stringContaining('/booking/reserva-123/processing-reservation?id_pago=pay-1'),
    }));
  });
});
