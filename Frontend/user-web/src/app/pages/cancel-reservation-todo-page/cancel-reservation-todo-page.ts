import { Location } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs';
import { BookingService } from '../../core/services/booking';
import type {
  BookingEstado,
  CancellationPolicyType,
  CancellationPreview,
  CancellationResult,
} from '../../models/reservation.interface';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HeaderComponent } from '../../shared/components/header/header';

type CancellationPageState =
  | 'loading'
  | 'loaded'
  | 'error'
  | 'notFound'
  | 'unauthorized'
  | 'notCancelable'
  | 'cancellationProcessing'
  | 'success';

@Component({
  selector: 'app-cancel-reservation-todo-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent],
  templateUrl: './cancel-reservation-todo-page.html',
  styleUrl: './cancel-reservation-todo-page.css',
})
export class CancelReservationTodoPage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly location = inject(Location);
  private readonly bookingService = inject(BookingService);

  readonly state = signal<CancellationPageState>('loading');
  readonly preview = signal<CancellationPreview | null>(null);
  readonly result = signal<CancellationResult | null>(null);
  readonly errorMessage = signal<string | null>(null);
  readonly reason = signal('');
  readonly warningOpen = signal(false);
  readonly acceptedTerms = signal(false);
  readonly submitting = signal(false);
  readonly reservationId = signal<string | null>(null);

  readonly canSubmit = computed(
    () =>
      !!this.preview()?.canCancel &&
      this.acceptedTerms() &&
      !this.submitting()
  );

  constructor() {
    this.loadPreview();
  }

  protected retry(): void {
    this.loadPreview();
  }

  protected goBack(): void {
    if (window.history.length > 1) {
      this.location.back();
      return;
    }

    const reservationId = this.reservationId();
    this.router.navigate(reservationId ? ['/mis-reservas', reservationId] : ['/mis-reservas']);
  }

  protected keepReservation(): void {
    const reservationId = this.reservationId();
    this.router.navigate(reservationId ? ['/mis-reservas', reservationId] : ['/mis-reservas']);
  }

  protected goHome(): void {
    this.router.navigate(['/']);
  }

  protected searchHotels(): void {
    this.router.navigate(['/']);
  }

  protected updateReason(event: Event): void {
    this.reason.set((event.target as HTMLTextAreaElement).value);
  }

  protected openWarning(): void {
    if (!this.preview()?.canCancel || this.submitting()) return;

    this.acceptedTerms.set(false);
    this.warningOpen.set(true);
  }

  protected closeWarning(): void {
    if (this.submitting()) return;

    this.warningOpen.set(false);
    this.acceptedTerms.set(false);
  }

  protected updateAcceptedTerms(event: Event): void {
    this.acceptedTerms.set((event.target as HTMLInputElement).checked);
  }

  protected confirmCancellation(): void {
    const reservationId = this.reservationId();
    if (!reservationId || !this.canSubmit()) return;

    this.submitting.set(true);
    this.errorMessage.set(null);

    const reason = this.reason().trim();
    this.bookingService.cancelReservation(reservationId, {
      acceptedTerms: true,
      ...(reason ? { reason } : {}),
    }).pipe(
      finalize(() => this.submitting.set(false))
    ).subscribe({
      next: (result) => this.handleCancellationResult(result),
      error: (error) => {
        this.warningOpen.set(false);
        this.errorMessage.set(this.resolveErrorMessage(error, 'No fue posible procesar la cancelacion. Intenta nuevamente.'));
        this.state.set(this.preview()?.canCancel ? 'loaded' : 'notCancelable');
      },
    });
  }

  protected formatDate(value: string | null): string {
    if (!value) return 'No disponible';

    const date = new Date(`${value}T00:00:00`);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }

  protected formatCurrency(amount: number | null | undefined, currency: string | null | undefined): string {
    if (amount === null || amount === undefined || !currency) return 'No disponible';

    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  protected formatStatus(status: BookingEstado | null | undefined): string {
    const labels: Partial<Record<BookingEstado, string>> = {
      HOLD: 'Hold',
      PENDIENTE: 'Pendiente',
      CONFIRMADA: 'Confirmada',
      CANCELACION_EN_PROCESO: 'Cancelacion en proceso',
      CANCELADA: 'Cancelada',
      EXPIRADA: 'Expirada',
    };
    return status ? labels[status] ?? status : 'No disponible';
  }

  protected isPolicyActive(type: CancellationPolicyType): boolean {
    return this.preview()?.cancellationPolicy.type === type;
  }

  protected getPolicyLabel(type: CancellationPolicyType): string {
    const labels: Record<CancellationPolicyType, string> = {
      FREE_CANCELLATION: 'Cancelacion gratuita',
      PARTIAL_REFUND: 'Reembolso parcial',
      NON_REFUNDABLE: 'No reembolsable',
    };
    return labels[type];
  }

  private loadPreview(): void {
    const reservationId = this.route.snapshot.paramMap.get('id_reserva');
    this.reservationId.set(reservationId);
    this.preview.set(null);
    this.result.set(null);
    this.errorMessage.set(null);
    this.warningOpen.set(false);
    this.acceptedTerms.set(false);

    if (!reservationId) {
      this.state.set('notFound');
      return;
    }

    this.state.set('loading');
    this.bookingService.getCancellationPreview(reservationId).subscribe({
      next: (preview) => this.handlePreview(preview),
      error: (error) => this.handlePreviewError(error),
    });
  }

  private handlePreview(preview: CancellationPreview): void {
    this.preview.set(preview);

    if (preview.currentStatus === 'CANCELACION_EN_PROCESO' || preview.pmsStatus === 'PENDING') {
      this.state.set('cancellationProcessing');
      return;
    }

    this.state.set(preview.canCancel ? 'loaded' : 'notCancelable');
  }

  private handlePreviewError(error: unknown): void {
    const status = error instanceof HttpErrorResponse ? error.status : undefined;
    this.errorMessage.set(this.resolveErrorMessage(error, 'No fue posible cargar la informacion de cancelacion.'));

    if (status === 401) {
      this.state.set('unauthorized');
      return;
    }

    if (status === 403) {
      this.state.set('unauthorized');
      return;
    }

    if (status === 404) {
      this.state.set('notFound');
      return;
    }

    this.state.set('error');
  }

  private handleCancellationResult(result: CancellationResult): void {
    this.result.set(result);
    this.warningOpen.set(false);

    if (result.reservationStatus === 'CANCELADA') {
      this.state.set('success');
      return;
    }

    this.state.set('cancellationProcessing');
  }

  private resolveErrorMessage(error: unknown, fallback: string): string {
    if (error instanceof HttpErrorResponse) {
      const payload = error.error;
      const backendMessage =
        typeof payload === 'string'
          ? payload
          : payload?.error ?? payload?.mensaje ?? payload?.detail;

      if (typeof backendMessage === 'string' && backendMessage.trim()) {
        return backendMessage.trim();
      }

      if (error.status === 401) return 'Debes iniciar sesion para continuar.';
      if (error.status === 403) return 'No tienes permiso para cancelar esta reserva.';
      if (error.status === 404) return 'La reserva solicitada no existe o ya no esta disponible.';
      if (error.status === 400) return 'La solicitud de cancelacion no es valida.';
      if (error.status === 409) return 'La reserva no puede cancelarse en su estado actual.';
      if (error.status === 0) return 'No fue posible contactar el servicio de cancelaciones.';
      if (error.status >= 500) return 'Ocurrio un error tecnico al procesar la solicitud.';
    }

    return fallback;
  }
}
