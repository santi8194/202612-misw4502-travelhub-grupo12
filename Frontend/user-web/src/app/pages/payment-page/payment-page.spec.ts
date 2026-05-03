import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { PaymentPage } from './payment-page';
import { PAYMENT_STORAGE_PREFIX } from '../../core/storage/payment-storage';

describe('PaymentPage', () => {
  let fixture: ComponentFixture<PaymentPage>;

  const routeStub = {
    snapshot: {
      paramMap: convertToParamMap({ id_reserva: 'reserva-123' }),
    },
  };

  beforeEach(async () => {
    sessionStorage.clear();

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
  });

  it('should show an error when payment intent is missing', () => {
    fixture = TestBed.createComponent(PaymentPage);
    fixture.detectChanges();

    const error = fixture.nativeElement.querySelector('[data-testid="payment-error"]');
    expect(error).toBeTruthy();
    expect(error.textContent).toContain('No se encontro una intencion de pago activa');
  });

  it('should render the Wompi widget script with required checkout fields', () => {
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

    const form: HTMLFormElement | null = fixture.nativeElement.querySelector('[data-testid="wompi-widget-form"]');
    const script = form?.querySelector('script[src="https://checkout.wompi.co/widget.js"]');

    expect(script).toBeTruthy();
    expect(script?.getAttribute('data-render')).toBe('button');
    expect(script?.getAttribute('data-public-key')).toBe('pub_test');
    expect(script?.getAttribute('data-currency')).toBe('COP');
    expect(script?.getAttribute('data-amount-in-cents')).toBe('12000000');
    expect(script?.getAttribute('data-reference')).toBe('PAY-1');
    expect(script?.getAttribute('data-signature:integrity')).toBe('sig');
    expect(script?.getAttribute('data-redirect-url')).toContain('/booking/reserva-123/processing-reservation?id_pago=pay-1');
  });
});
