import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, ElementRef, OnInit, ViewChild, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { PaymentIntentResponse } from '../../core/services/booking';
import { PAYMENT_STORAGE_PREFIX } from '../../core/storage/payment-storage';
import { I18nService } from '../../core/i18n/i18n.service';
import { TranslatePipe } from '../../shared/pipes/translate.pipe';
import { CurrencyService } from '../../core/services/currency.service';

@Component({
  selector: 'app-payment-page',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent, TranslatePipe],
  templateUrl: './payment-page.html',
  styleUrl: './payment-page.css',
})
export class PaymentPage implements OnInit, AfterViewInit {
  private readonly route = inject(ActivatedRoute);
  private readonly i18n = inject(I18nService);
  protected readonly currency = inject(CurrencyService);

  @ViewChild('wompiWidgetForm') private readonly wompiWidgetForm?: ElementRef<HTMLFormElement>;

  readonly reservationId = this.route.snapshot.paramMap.get('id_reserva') ?? '';
  readonly payment = signal<PaymentIntentResponse | null>(null);
  readonly error = signal<string | null>(null);
  readonly isWidgetReady = signal(false);
  readonly widgetRenderId = signal(0);

  ngOnInit(): void {
    this.loadPayment();
  }

  ngAfterViewInit(): void {
    this.renderWompiWidget();
  }

  readonly amountLabel = () => {
    const current = this.payment();
    if (!current) {
      return '';
    }

    return this.currency.format(Math.round(current.monto), current.moneda);
  };

  private loadPayment(): void {
    if (!this.reservationId) {
      this.error.set(this.i18n.translate('payment.identifyReservationMissing'));
      return;
    }

    const rawPayment = sessionStorage.getItem(this.storageKey());
    if (!rawPayment) {
      this.error.set(this.i18n.translate('payment.activeIntentMissing'));
      return;
    }

    try {
      const payment = JSON.parse(rawPayment) as PaymentIntentResponse;
      if (!payment.checkout) {
        this.error.set(this.i18n.translate('payment.checkoutMissing'));
        return;
      }

      this.payment.set(payment);
      this.renderWompiWidget();
    } catch {
      this.error.set(this.i18n.translate('payment.readError'));
    }
  }

  private buildWidgetAttributes(payment: PaymentIntentResponse): Record<string, string> {
    const checkout = payment.checkout;
    if (!checkout) {
      throw new Error('Payment checkout is required');
    }

    return {
      'data-render': 'button',
      'data-public-key': checkout.public_key,
      'data-currency': checkout.currency,
      'data-amount-in-cents': String(checkout.amount_in_cents),
      'data-reference': checkout.reference,
      'data-signature:integrity': checkout.signature_integrity,
      'data-redirect-url': `${window.location.origin}/booking/${this.reservationId}/processing-reservation?id_pago=${encodeURIComponent(payment.id_pago)}`,
    };
  }

  private renderWompiWidget(): void {
    const payment = this.payment();
    const form = this.wompiWidgetForm?.nativeElement;
    if (!payment?.checkout || !form) {
      return;
    }

    form.replaceChildren();
    this.isWidgetReady.set(false);
    this.error.set(null);

    try {
      const script = document.createElement('script');
      script.src = 'https://checkout.wompi.co/widget.js';
      script.async = true;
      script.onload = () => this.isWidgetReady.set(true);
      script.onerror = () => {
        this.error.set(this.i18n.translate('payment.widgetLoadError'));
        this.isWidgetReady.set(false);
      };

      for (const [name, value] of Object.entries(this.buildWidgetAttributes(payment))) {
        script.setAttribute(name, value);
      }

      form.appendChild(script);
      this.widgetRenderId.update((current) => current + 1);
    } catch (error) {
      console.error('[PaymentPage] Wompi widget render error', error);
      this.error.set(this.i18n.translate('payment.widgetPrepareError'));
    }
  }

  private storageKey(): string {
    return `${PAYMENT_STORAGE_PREFIX}${this.reservationId}`;
  }
}
