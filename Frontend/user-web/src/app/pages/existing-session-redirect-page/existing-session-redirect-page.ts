import { Component, OnDestroy, inject, signal } from '@angular/core';
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
export class ExistingSessionRedirectPage implements OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly bookingService = inject(BookingService);

  private redirectTimeout: ReturnType<typeof setTimeout> | null = null;

  readonly targetReservationId = this.route.snapshot.queryParamMap.get('reservationId') ?? '';
  isRedirecting = signal(true);
  statusMessage = signal('Estamos validando el estado de tu reserva activa...');
  hasResolutionError = signal(false);

  constructor() {
    if (!this.targetReservationId) {
      this.isRedirecting.set(false);
      this.hasResolutionError.set(true);
      this.statusMessage.set('No encontramos una sesión activa para redirigirte.');
      return;
    }

    this.redirectTimeout = setTimeout(() => {
      this.resolveAndRedirect();
    }, 900);
  }

  ngOnDestroy(): void {
    if (this.redirectTimeout !== null) {
      clearTimeout(this.redirectTimeout);
      this.redirectTimeout = null;
    }
  }

  private resolveAndRedirect(): void {
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
          this.statusMessage.set('Tu reserva sigue activa en HOLD. Te llevamos al carrito para continuar.');
          this.goToActiveSession();
          return;
        }

        if (status === 'PENDIENTE') {
          this.statusMessage.set('Tu reserva está siendo procesada. Te llevamos a la vista de seguimiento.');
          this.router.navigate(['/booking', this.targetReservationId, 'processing-reservation']);
          return;
        }

        if (status === 'CONFIRMADA') {
          this.statusMessage.set('Tu reserva ya fue confirmada.');
          this.router.navigate(['/booking', this.targetReservationId, 'confirm-reservation'], {
            queryParams: {
              status: 'confirmed',
              reason: 'Tu reserva ya estaba confirmada.',
            },
          });
          return;
        }

        if (status === 'CANCELADA') {
          const reason = response?.motivo
            ?? response?.mensaje
            ?? response?.detail
            ?? response?.error
            ?? 'Tu reserva ya estaba cancelada. Puedes buscar una nueva opción.';
          this.statusMessage.set('Tu reserva ya estaba cancelada.');
          this.router.navigate(['/booking', this.targetReservationId, 'confirm-reservation'], {
            queryParams: {
              status: 'rejected',
              reason,
            },
          });
          return;
        }

        this.hasResolutionError.set(true);
        this.statusMessage.set('No pudimos determinar el estado de tu sesión activa. Puedes abrirla manualmente.');
      },
      error: () => {
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

    this.router.navigate(['/booking', this.targetReservationId]);
  }
}
