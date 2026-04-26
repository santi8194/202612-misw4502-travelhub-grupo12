import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';

interface BookingStatusResponse {
  estado?: string;
  motivo?: string;
  mensaje?: string;
  detail?: string;
  error?: string;
}

@Component({
  selector: 'app-existing-session-redirect-page',
  standalone: true,
  imports: [RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './existing-session-redirect-page.html',
  styleUrl: './existing-session-redirect-page.css',
})
export class ExistingSessionRedirectPage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly bookingService = inject(BookingService);

  readonly targetReservationId = this.route.snapshot.queryParamMap.get('reservationId') ?? '';
  isRedirecting = signal(true);
  statusMessage = signal('Estamos validando el estado de tu reserva activa...');
  hasResolutionError = signal(false);

  private resolvedStatus = signal<'hold' | 'pending' | 'confirmed' | 'cancelled' | 'unknown' | 'error' | null>(null);
  private resolvedReason = signal('');

  constructor() {
    if (!this.targetReservationId) {
      this.isRedirecting.set(false);
      this.hasResolutionError.set(true);
      this.statusMessage.set('No encontramos una sesión activa para redirigirte.');
      return;
    }

    this.resolveSessionState();
  }

  private resolveSessionState(): void {
    if (!this.targetReservationId) {
      this.isRedirecting.set(false);
      this.hasResolutionError.set(true);
      this.statusMessage.set('No encontramos una sesión activa para redirigirte.');
      return;
    }

    this.bookingService.getBookingById(this.targetReservationId).pipe(
      finalize(() => this.isRedirecting.set(false))
    ).subscribe({
      next: (response: BookingStatusResponse) => {
        const status = (response?.estado ?? '').toUpperCase().trim();

        if (status === 'HOLD') {
          this.resolvedStatus.set('hold');
          this.statusMessage.set('Tu reserva sigue activa en HOLD. Puedes abrirla para continuar en el carrito.');
          return;
        }

        if (status === 'PENDIENTE') {
          this.resolvedStatus.set('pending');
          this.statusMessage.set('Tu reserva esta siendo procesada. Puedes abrir la vista de seguimiento.');
          return;
        }

        if (status === 'CONFIRMADA') {
          this.resolvedStatus.set('confirmed');
          this.statusMessage.set('Tu reserva ya fue confirmada.');
          return;
        }

        if (status === 'CANCELADA') {
          this.resolvedStatus.set('cancelled');
          const reason = response?.motivo
            ?? response?.mensaje
            ?? response?.detail
            ?? response?.error
            ?? 'Tu reserva ya estaba cancelada. Puedes buscar una nueva opcion.';
          this.resolvedReason.set(reason);
          this.statusMessage.set('Tu reserva ya estaba cancelada.');
          return;
        }

        this.resolvedStatus.set('unknown');
        this.hasResolutionError.set(true);
        this.statusMessage.set('No pudimos determinar el estado de tu sesion activa. Puedes abrirla manualmente.');
      },
      error: () => {
        this.resolvedStatus.set('error');
        this.hasResolutionError.set(true);
        this.statusMessage.set('No fue posible validar el estado de la reserva en este momento. Puedes abrirla manualmente.');
      },
    });
  }

  goToActiveSession(): void {
    if (!this.targetReservationId) {
      this.router.navigate(['/resultados']);
      return;
    }

    const status = this.resolvedStatus();
    if (status === 'pending') {
      this.router.navigate(['/booking', this.targetReservationId, 'processing-reservation']);
      return;
    }

    if (status === 'confirmed') {
      this.router.navigate(['/booking', this.targetReservationId, 'confirm-reservation'], {
        queryParams: {
          status: 'confirmed',
          reason: 'Tu reserva ya estaba confirmada.',
        },
      });
      return;
    }

    if (status === 'cancelled') {
      this.router.navigate(['/booking', this.targetReservationId, 'confirm-reservation'], {
        queryParams: {
          status: 'rejected',
          reason: this.resolvedReason() || 'Tu reserva ya estaba cancelada. Puedes buscar una nueva opcion.',
        },
      });
      return;
    }

    this.router.navigate(['/booking', this.targetReservationId]);
  }

  actionLabel(): string {
    const status = this.resolvedStatus();
    if (status === 'pending') {
      return 'Abrir seguimiento de reserva';
    }

    if (status === 'confirmed') {
      return 'Ver confirmacion de reserva';
    }

    if (status === 'cancelled') {
      return 'Ver detalle de reserva cancelada';
    }

    return 'Ir ahora a mi sesion activa';
  }
}
