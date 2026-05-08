import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ReservationViewModel, ReservationStatus } from '../../../models/reservation.interface';
import { getStatusLabel } from '../../../core/services/reservation-status.resolver';

@Component({
  selector: 'app-reservation-card',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './reservation-card.html',
  styleUrl: './reservation-card.css',
})
export class ReservationCardComponent {
  reservation = input.required<ReservationViewModel>();

  protected readonly getStatusLabel = getStatusLabel;

  protected formatDate(dateStr: string): string {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }

  protected formatCurrency(amount: number | null, moneda: string): string {
    if (amount === null) return '—';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: moneda,
      maximumFractionDigits: 0,
    }).format(amount);
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

  protected showCompletarPago(estado: ReservationStatus): boolean {
    return estado === 'PENDIENTE_PAGO';
  }

  protected showCancelarReserva(estado: ReservationStatus): boolean {
    return estado === 'CONFIRMADA' || estado === 'PENDIENTE_CONFIRMACION_HOTEL';
  }
}
