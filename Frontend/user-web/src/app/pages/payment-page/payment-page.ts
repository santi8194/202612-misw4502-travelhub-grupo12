import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { PaymentIntentResponse } from '../../core/services/booking';
import { PAYMENT_STORAGE_PREFIX } from '../../core/storage/payment-storage';

@Component({
  selector: 'app-payment-page',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './payment-page.html',
  styleUrl: './payment-page.css',
})
export class PaymentPage implements AfterViewInit, OnDestroy {
  @ViewChild('wompiWidget', { static: true })
  private readonly widgetRef!: ElementRef<HTMLDivElement>;

  private readonly route = inject(ActivatedRoute);

  readonly reservationId = this.route.snapshot.paramMap.get('id_reserva') ?? '';
  readonly payment = signal<PaymentIntentResponse | null>(null);
  readonly error = signal<string | null>(null);

  ngAfterViewInit(): void {
    this.loadPayment();
  }

  ngOnDestroy(): void {
    this.clearWidget();
  }

  readonly amountLabel = () => {
    const current = this.payment();
    if (!current) {
      return '';
    }

    return `${current.moneda} ${Math.round(current.monto).toLocaleString('es-CO')}`;
  };

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
      this.renderWidget(payment);
    } catch {
      this.error.set('No fue posible leer la intencion de pago.');
    }
  }

  private renderWidget(payment: PaymentIntentResponse): void {
    const checkout = payment.checkout;
    if (!checkout) {
      return;
    }

    const redirectUrl = `${window.location.origin}/booking/${this.reservationId}/processing-reservation?id_pago=${encodeURIComponent(payment.id_pago)}`;
    const form = document.createElement('form');
    const script = document.createElement('script');

    script.src = 'https://checkout.wompi.co/widget.js';
    script.setAttribute('data-render', 'button');
    script.setAttribute('data-public-key', checkout.public_key);
    script.setAttribute('data-currency', checkout.currency);
    script.setAttribute('data-amount-in-cents', String(checkout.amount_in_cents));
    script.setAttribute('data-reference', checkout.reference);
    script.setAttribute('data-signature:integrity', checkout.signature_integrity);
    script.setAttribute('data-redirect-url', redirectUrl);

    form.appendChild(script);
    this.widgetRef.nativeElement.appendChild(form);
  }

  private clearWidget(): void {
    this.widgetRef.nativeElement.replaceChildren();
  }

  private storageKey(): string {
    return `${PAYMENT_STORAGE_PREFIX}${this.reservationId}`;
  }
}
