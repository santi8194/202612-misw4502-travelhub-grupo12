import { Component, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ReservationViewModel, ReservationStatus } from '../../../models/reservation.interface';
import { getStatusTranslationKey } from '../../../core/services/reservation-status.resolver';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../pipes/translate.pipe';
import { CurrencyService } from '../../../core/services/currency.service';

@Component({
  selector: 'app-reservation-card',
  standalone: true,
  imports: [RouterLink, TranslatePipe],
  templateUrl: './reservation-card.html',
  styleUrl: './reservation-card.css',
})
export class ReservationCardComponent {
  private readonly i18n = inject(I18nService);
  protected readonly currency = inject(CurrencyService);
  reservation = input.required<ReservationViewModel>();

  protected formatDate(dateStr: string): string {
    return this.i18n.formatDate(dateStr);
  }

  protected formatCurrency(amount: number | null, moneda: string): string {
    if (amount === null) return '—';
    return this.currency.format(amount, moneda);
  }

  protected getStatusClass(estado: ReservationStatus): string {
    const map: Record<ReservationStatus, string> = {
      CONFIRMADA: 'badge--confirmada',
      PENDIENTE_PAGO: 'badge--pendiente-pago',
      PENDIENTE_CONFIRMACION_HOTEL: 'badge--pendiente-hotel',
      CANCELADA: 'badge--cancelada',
    };
    return map[estado];
  }

  protected getStatusLabel(estado: ReservationStatus): string {
    return this.i18n.translate(getStatusTranslationKey(estado));
  }

  protected getConfirmationCode(idReserva: string): string {
    return idReserva.replace(/[^a-z0-9]/gi, '').slice(0, 6).toUpperCase();
  }

  protected showCompletarPago(estado: ReservationStatus): boolean {
    return estado === 'PENDIENTE_PAGO';
  }

  protected showCancelarReserva(estado: ReservationStatus): boolean {
    return estado === 'CONFIRMADA' || estado === 'PENDIENTE_CONFIRMACION_HOTEL';
  }
}
