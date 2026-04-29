import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { PaymentIntentResponse } from '../../core/services/booking';
import { PAYMENT_STORAGE_PREFIX } from '../../core/storage/payment-storage';

declare global {
  interface Window {
    WidgetCheckout?: new (config: WompiCheckoutConfig) => {
      open(callback: (result: WompiCheckoutResult) => void): void;
    };
  }
}

interface WompiCheckoutConfig {
  currency: string;
  amountInCents: number;
  reference: string;
  publicKey: string;
  signature: {
    integrity: string;
  };
  redirectUrl?: string;
}

interface WompiCheckoutResult {
  transaction?: {
    id?: string;
    status?: string;
  };
}

@Component({
  selector: 'app-payment-page',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './payment-page.html',
  styleUrl: './payment-page.css',
})
export class PaymentPage implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly reservationId = this.route.snapshot.paramMap.get('id_reserva') ?? '';
  readonly payment = signal<PaymentIntentResponse | null>(null);
  readonly error = signal<string | null>(null);
  readonly widgetWarning = signal<string | null>(null);
  readonly isWidgetReady = signal(false);
  readonly isOpeningWidget = signal(false);
  readonly checkoutForm = signal<Record<string, string> | null>(null);

  ngOnInit(): void {
    this.loadPayment();
  }

  readonly amountLabel = () => {
    const current = this.payment();
    if (!current) {
      return '';
    }

    return `${current.moneda} ${Math.round(current.monto).toLocaleString('es-CO')}`;
  };

  openWidget(): void {
    const payment = this.payment();
    if (!payment?.checkout || !window.WidgetCheckout || this.isOpeningWidget()) {
      return;
    }

    this.isOpeningWidget.set(true);
    this.error.set(null);
    this.widgetWarning.set(null);

    try {
      const checkout = new window.WidgetCheckout(this.buildCheckoutConfig(payment));
      checkout.open((result) => {
        this.router.navigate(['/booking', this.reservationId, 'processing-reservation'], {
          queryParams: {
            id_pago: payment.id_pago,
            transaction_id: result.transaction?.id ?? null,
            status: result.transaction?.status ?? null,
          },
        });
      });
      window.setTimeout(() => this.warnIfWidgetDidNotRender(), 1500);
    } catch (error) {
      console.error('[PaymentPage] Wompi widget open error', error);
      this.error.set('No fue posible abrir el widget de Wompi. Puedes intentar de nuevo.');
    } finally {
      this.isOpeningWidget.set(false);
    }
  }

  private loadPayment(): void {
    if (!this.reservationId) {
      this.error.set('No se encontro el identificador de la reserva.');
      return;
    }

    const rawPayment = sessionStorage.getItem(this.storageKey());
    if (!rawPayment) {
      this.error.set('No se encontro una intencion de pago activa para esta reserva.');
      return;
    }

    try {
      const payment = JSON.parse(rawPayment) as PaymentIntentResponse;
      if (!payment.checkout) {
        this.error.set('La intencion de pago no contiene datos de checkout.');
        return;
      }

      this.payment.set(payment);
      this.checkoutForm.set(this.buildCheckoutForm(payment));
      this.waitForWidgetScript();
    } catch {
      this.error.set('No fue posible leer la intencion de pago.');
    }
  }

  private buildCheckoutConfig(payment: PaymentIntentResponse): WompiCheckoutConfig {
    const checkout = payment.checkout;
    if (!checkout) {
      throw new Error('Payment checkout is required');
    }

    return {
      currency: checkout.currency,
      amountInCents: checkout.amount_in_cents,
      reference: checkout.reference,
      publicKey: checkout.public_key,
      signature: {
        integrity: checkout.signature_integrity,
      },
      redirectUrl: `${window.location.origin}/booking/${this.reservationId}/processing-reservation?id_pago=${encodeURIComponent(payment.id_pago)}`,
    };
  }

  private buildCheckoutForm(payment: PaymentIntentResponse): Record<string, string> {
    const checkout = payment.checkout;
    if (!checkout) {
      throw new Error('Payment checkout is required');
    }

    return {
      'public-key': checkout.public_key,
      currency: checkout.currency,
      'amount-in-cents': String(checkout.amount_in_cents),
      reference: checkout.reference,
      'signature:integrity': checkout.signature_integrity,
      'redirect-url': `${window.location.origin}/booking/${this.reservationId}/processing-reservation?id_pago=${encodeURIComponent(payment.id_pago)}`,
    };
  }

  private waitForWidgetScript(retries = 20): void {
    if (window.WidgetCheckout) {
      this.isWidgetReady.set(true);
      return;
    }

    if (retries <= 0) {
      this.error.set('No fue posible cargar el widget de Wompi. Intenta con el checkout web.');
      return;
    }

    window.setTimeout(() => this.waitForWidgetScript(retries - 1), 250);
  }

  private warnIfWidgetDidNotRender(): void {
    const wompiElement = document.querySelector(
      'iframe[src*="wompi"], iframe[src*="checkout"], [class*="wompi"], [id*="wompi"]'
    );
    if (!wompiElement) {
      this.widgetWarning.set('Wompi no desplegó el widget. Esto suele pasar cuando la llave pública, la firma de integridad o la referencia no son aceptadas por Wompi. Prueba el checkout web y revisa la configuración de secretos en EKS.');
    }
  }

  private storageKey(): string {
    return `${PAYMENT_STORAGE_PREFIX}${this.reservationId}`;
  }
}
