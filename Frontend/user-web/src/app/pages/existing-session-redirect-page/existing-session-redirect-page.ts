import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { I18nService } from '../../core/i18n/i18n.service';
import { TranslatePipe } from '../../shared/pipes/translate.pipe';

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
  imports: [RouterLink, HeaderComponent, FooterComponent, TranslatePipe],
  templateUrl: './existing-session-redirect-page.html',
  styleUrl: './existing-session-redirect-page.css',
})
export class ExistingSessionRedirectPage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly bookingService = inject(BookingService);
  private readonly i18n = inject(I18nService);

  readonly targetReservationId = this.route.snapshot.queryParamMap.get('reservationId') ?? '';
  isRedirecting = signal(true);
  statusMessage = signal(this.i18n.translate('processing.message'));
  hasResolutionError = signal(false);

  private resolvedStatus = signal<'hold' | 'pending' | 'confirmed' | 'cancelled' | 'unknown' | 'error' | null>(null);
  private resolvedReason = signal('');

  constructor() {
    if (!this.targetReservationId) {
      this.isRedirecting.set(false);
      this.hasResolutionError.set(true);
      this.statusMessage.set(this.i18n.translate('existingSession.error'));
      return;
    }

    this.resolveSessionState();
  }

  private resolveSessionState(): void {
    if (!this.targetReservationId) {
      this.isRedirecting.set(false);
      this.hasResolutionError.set(true);
      this.statusMessage.set(this.i18n.translate('existingSession.error'));
      return;
    }

    this.bookingService.getBookingById(this.targetReservationId).pipe(
      finalize(() => this.isRedirecting.set(false))
    ).subscribe({
      next: (response: BookingStatusResponse) => {
        const status = (response?.estado ?? '').toUpperCase().trim();

        if (status === 'HOLD') {
          this.resolvedStatus.set('hold');
          this.statusMessage.set(this.i18n.translate('processing.sagaProcessing'));
          return;
        }

        if (status === 'PENDIENTE') {
          this.resolvedStatus.set('pending');
          this.statusMessage.set(this.i18n.translate('processing.message'));
          return;
        }

        if (status === 'CONFIRMADA') {
          this.resolvedStatus.set('confirmed');
          this.statusMessage.set(this.i18n.translate('processing.confirmed'));
          return;
        }

        if (status === 'CANCELADA') {
          this.resolvedStatus.set('cancelled');
          const reason = response?.motivo
            ?? response?.mensaje
            ?? response?.detail
            ?? response?.error
            ?? this.i18n.translate('processing.cancelled');
          this.resolvedReason.set(reason);
          this.statusMessage.set(this.i18n.translate('processing.cancelled'));
          return;
        }

        this.resolvedStatus.set('unknown');
        this.hasResolutionError.set(true);
        this.statusMessage.set(this.i18n.translate('existingSession.error'));
      },
      error: () => {
        this.resolvedStatus.set('error');
        this.hasResolutionError.set(true);
        this.statusMessage.set(this.i18n.translate('existingSession.error'));
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
          reason: this.i18n.translate('processing.confirmed'),
        },
      });
      return;
    }

    if (status === 'cancelled') {
      this.router.navigate(['/booking', this.targetReservationId, 'confirm-reservation'], {
        queryParams: {
          status: 'rejected',
          reason: this.resolvedReason() || this.i18n.translate('processing.cancelled'),
        },
      });
      return;
    }

    this.router.navigate(['/booking', this.targetReservationId]);
  }

  actionLabel(): string {
    const status = this.resolvedStatus();
    if (status === 'pending') {
      return this.i18n.translate('existingSession.goToActive');
    }

    if (status === 'confirmed') {
      return this.i18n.translate('existingSession.goToActive');
    }

    if (status === 'cancelled') {
      return this.i18n.translate('existingSession.goToActive');
    }

    return this.i18n.translate('existingSession.openAnyway');
  }
}
