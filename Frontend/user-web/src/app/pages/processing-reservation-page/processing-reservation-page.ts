import { Component, OnDestroy, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';

interface BookingStatusResponse {
  estado?: string;
  mensaje?: string;
  detail?: string;
  error?: string;
  motivo?: string;
}

@Component({
  selector: 'app-processing-reservation-page',
  standalone: true,
  imports: [RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './processing-reservation-page.html',
  styleUrl: './processing-reservation-page.css',
})
export class ProcessingReservationPage implements OnDestroy {
  private static readonly POLLING_INTERVAL_MS = 3000;

  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly bookingService = inject(BookingService);

  private pollingId: ReturnType<typeof setInterval> | null = null;
  private isRequestInFlight = false;
  private hasResolved = false;

  readonly reservationId = this.route.snapshot.paramMap.get('id_reserva') ?? '';
  readonly initialReason = this.route.snapshot.queryParamMap.get('reason') ?? '';

  status = signal('PENDIENTE');
  isPolling = signal(true);
  pollingError = signal<string | null>(null);

  readonly message = computed(() => {
    if (this.pollingError()) {
      return this.pollingError();
    }

    if (this.initialReason.trim()) {
      return this.sanitizeUserMessage(this.initialReason);
    }

    return 'Tu reserva está en proceso. Estamos confirmando el resultado con hoteles y pagos.';
  });

  constructor() {
    if (!this.reservationId) {
      this.isPolling.set(false);
      this.pollingError.set('No se encontró el identificador de reserva para consultar el estado.');
      return;
    }

    this.pollStatus();
    this.pollingId = setInterval(() => this.pollStatus(), ProcessingReservationPage.POLLING_INTERVAL_MS);
  }

  ngOnDestroy(): void {
    this.clearPolling();
  }

  private pollStatus(): void {
    if (!this.reservationId || this.hasResolved || this.isRequestInFlight) {
      return;
    }

    this.isRequestInFlight = true;
    this.bookingService.getBookingById(this.reservationId).pipe(
      finalize(() => {
        this.isRequestInFlight = false;
      })
    ).subscribe({
      next: (response: BookingStatusResponse) => this.handleStatusResponse(response),
      error: () => {
        this.pollingError.set('No pudimos consultar el estado de la reserva. Reintentando...');
      },
    });
  }

  private handleStatusResponse(response: BookingStatusResponse): void {
    const normalizedStatus = (response?.estado ?? '').toUpperCase().trim();
    if (normalizedStatus) {
      this.status.set(normalizedStatus);
    }

    if (normalizedStatus === 'CONFIRMADA') {
      this.resolveAndNavigate('confirmed', 'Reserva confirmada exitosamente.');
      return;
    }

    if (normalizedStatus === 'CANCELADA') {
      const rawReason = response?.motivo
        ?? response?.mensaje
        ?? response?.detail
        ?? response?.error
        ?? 'La reserva no pudo ser confirmada.';
      const reason = this.buildCancellationReason(rawReason);
      this.resolveAndNavigate('rejected', reason);
      return;
    }

    this.pollingError.set(null);
  }

  private resolveAndNavigate(status: 'confirmed' | 'rejected', reason: string): void {
    if (this.hasResolved) {
      return;
    }

    this.hasResolved = true;
    this.isPolling.set(false);
    this.clearPolling();

    this.router.navigate(['/booking', this.reservationId, 'confirm-reservation'], {
      queryParams: {
        status,
        reason,
      },
    });
  }

  private buildCancellationReason(rawReason: string): string {
    const trimmed = rawReason.trim();
    if (!trimmed) {
      return 'No fue posible confirmar tu reserva porque la validación con hoteles o pagos no se completó correctamente. Te recomendamos volver al carrito e intentarlo nuevamente con otra opción.';
    }

    const sanitized = this.sanitizeUserMessage(trimmed);

    const normalized = sanitized
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();

    if (normalized.includes('cancelada durante el procesamiento de la saga')) {
      return 'No pudimos confirmar tu reserva porque una de las validaciones de hoteles o pagos fue rechazada durante el proceso. Puedes volver al carrito para intentarlo de nuevo o elegir otra opción de reserva.';
    }

    return sanitized;
  }

  private sanitizeUserMessage(message: string): string {
    const normalized = message
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();

    if (normalized.includes('saga')) {
      if (normalized.includes('iniciando')) {
        return 'Tu reserva fue formalizada. Estamos confirmando la disponibilidad y el pago.';
      }

      return 'Estamos procesando tu reserva. En breve te mostraremos el resultado.';
    }

    return message;
  }

  private clearPolling(): void {
    if (this.pollingId !== null) {
      clearInterval(this.pollingId);
      this.pollingId = null;
    }
  }
}
