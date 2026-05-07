import { Location } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { BookingService } from '../../core/services/booking';
import { CatalogService } from '../../core/services/catalog';
import { AuthService } from '../../core/services/auth';
import { getStatusLabel, resolveReservationStatus } from '../../core/services/reservation-status.resolver';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HeaderComponent } from '../../shared/components/header/header';
import type { BookingReservation, PaymentInfo, ReservationStatus } from '../../models/reservation.interface';
import type { RoomDetailResponse } from '../../models/room-detail.interface';

interface ReservationDetail {
  id: string;
  hotelName: string;
  location: {
    city: string;
    country: string;
  };
  checkInDate: string;
  checkOutDate: string;
  guests: number;
  confirmationNumber: string | null;
  status: ReservationStatus;
  totalAmount: number | null;
  currency: string;
  images: string[];
  canCancel: boolean;
  cancellationReason?: string;
}

@Component({
  selector: 'app-reservation-detail-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent],
  templateUrl: './reservation-detail-page.html',
  styleUrl: './reservation-detail-page.css',
})
export class ReservationDetailPage {
  private static readonly DEFAULT_USER_COUNTRY = 'Colombia';

  private readonly route = inject(ActivatedRoute);
  private readonly location = inject(Location);
  private readonly router = inject(Router);
  private readonly http = inject(HttpClient);
  private readonly bookingService = inject(BookingService);
  private readonly catalogService = inject(CatalogService);
  private readonly authService = inject(AuthService);
  private readonly paymentApiUrl = environment.paymentApiUrl;

  readonly loading = signal(true);
  readonly detail = signal<ReservationDetail | null>(null);
  readonly error = signal<string | null>(null);
  readonly notFound = signal(false);
  readonly unauthorized = signal(false);
  readonly totalLoading = signal(false);
  readonly totalUnavailable = signal(false);
  readonly currentImageIndex = signal(0);
  readonly imageLoadFailed = signal(false);
  private readonly cancellationPolicyDays = signal(0);
  readonly currentImageUrl = computed(() => {
    const images = this.detail()?.images ?? [];
    return images[this.currentImageIndex()] ?? '';
  });

  constructor() {
    this.loadReservationDetail();
  }

  protected goBack(): void {
    if (window.history.length > 1) {
      this.location.back();
      return;
    }

    this.router.navigate(['/mis-reservas']);
  }

  protected retry(): void {
    this.loadReservationDetail();
  }

  protected previousImage(): void {
    const total = this.detail()?.images.length ?? 0;
    if (total <= 1) return;

    this.imageLoadFailed.set(false);
    this.currentImageIndex.update(index => index === 0 ? total - 1 : index - 1);
  }

  protected nextImage(): void {
    const total = this.detail()?.images.length ?? 0;
    if (total <= 1) return;

    this.imageLoadFailed.set(false);
    this.currentImageIndex.update(index => index === total - 1 ? 0 : index + 1);
  }

  protected goToImage(index: number): void {
    const total = this.detail()?.images.length ?? 0;
    if (index < 0 || index >= total) return;

    this.imageLoadFailed.set(false);
    this.currentImageIndex.set(index);
  }

  protected onImageError(): void {
    this.imageLoadFailed.set(true);
  }

  protected startCancellation(): void {
    const reservationId = this.detail()?.id;
    if (!reservationId) return;

    this.router.navigate(['/mis-reservas', reservationId, 'cancelar']);
  }

  private loadReservationDetail(): void {
    const reservationId = this.route.snapshot.paramMap.get('id_reserva');

    this.loading.set(true);
    this.detail.set(null);
    this.error.set(null);
    this.notFound.set(false);
    this.unauthorized.set(false);
    this.totalLoading.set(false);
    this.totalUnavailable.set(false);
    this.currentImageIndex.set(0);
    this.imageLoadFailed.set(false);
    this.cancellationPolicyDays.set(0);

    if (!reservationId) {
      this.notFound.set(true);
      this.loading.set(false);
      return;
    }

    this.bookingService.getBookingById(reservationId).subscribe({
      next: (booking: BookingReservation) => this.handleBookingLoaded(booking),
      error: (err) => this.handleBookingError(err),
    });
  }

  private handleBookingLoaded(booking: BookingReservation): void {
    const currentUserId = this.authService.getCurrentUserId();
    if (!currentUserId || booking.id_usuario !== currentUserId) {
      this.unauthorized.set(true);
      this.loading.set(false);
      return;
    }

    if (!booking.id_categoria) {
      this.error.set('La reserva no tiene información de hospedaje disponible.');
      this.loading.set(false);
      return;
    }

    this.catalogService.getCategoryViewDetail(booking.id_categoria).subscribe({
      next: (catalog) => {
        this.detail.set(this.buildReservationDetail(booking, catalog));
        this.loading.set(false);
        this.resolveTotal(booking);
      },
      error: () => {
        this.error.set('No fue posible cargar la información del hospedaje.');
        this.loading.set(false);
      },
    });
  }

  private handleBookingError(error: unknown): void {
    if (this.isNotFoundError(error)) {
      this.notFound.set(true);
    } else {
      this.error.set('No fue posible cargar el detalle de la reserva.');
    }

    this.loading.set(false);
  }

  private buildReservationDetail(
    booking: BookingReservation,
    catalog: RoomDetailResponse
  ): ReservationDetail {
    const images = [...(catalog.galeria ?? [])]
      .sort((a, b) => a.orden - b.orden)
      .map(image => image.url_full)
      .filter(url => !!url);

    const status = resolveReservationStatus(booking.estado, null);
    const policyDays = catalog.categoria.politica_cancelacion?.dias_anticipacion ?? 0;
    this.cancellationPolicyDays.set(policyDays);
    const cancellation = this.resolveCancellation(status, booking.fecha_check_in, policyDays);

    return {
      id: booking.id_reserva,
      hotelName: catalog.categoria.nombre_comercial,
      location: {
        city: catalog.propiedad.ubicacion.ciudad,
        country: catalog.propiedad.ubicacion.pais,
      },
      checkInDate: booking.fecha_check_in,
      checkOutDate: booking.fecha_check_out,
      guests: this.getGuestCount(booking),
      confirmationNumber: booking.codigo_confirmacion_ota || booking.codigo_localizador_pms || null,
      status,
      totalAmount: null,
      currency: catalog.categoria.precio_base.moneda,
      images,
      canCancel: cancellation.canCancel,
      cancellationReason: cancellation.reason,
    };
  }

  private resolveCancellation(
    status: ReservationStatus,
    checkInDateValue: string,
    policyDays: number
  ): { canCancel: boolean; reason?: string } {
    if (status !== 'CONFIRMADA' && status !== 'PENDIENTE_CONFIRMACION_HOTEL') {
      return { canCancel: false, reason: 'Esta reserva no se puede cancelar por su estado actual.' };
    }

    const checkInDate = new Date(checkInDateValue + 'T00:00:00');
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const millisecondsPerDay = 24 * 60 * 60 * 1000;
    const daysUntilCheckIn = Math.ceil((checkInDate.getTime() - today.getTime()) / millisecondsPerDay);

    if (daysUntilCheckIn < policyDays) {
      return {
        canCancel: false,
        reason: `Esta reserva requiere ${policyDays} días de anticipación para cancelar.`,
      };
    }

    return { canCancel: true };
  }

  private resolveTotal(booking: BookingReservation): void {
    this.totalLoading.set(true);
    this.totalUnavailable.set(false);

    this.http.get<PaymentInfo>(
      `${this.paymentApiUrl}/payments/by-reserva/${booking.id_reserva}`
    ).subscribe({
      next: (payment) => {
        if (payment?.estado === 'APPROVED') {
          this.updateDetailTotal(payment.monto, payment.moneda, resolveReservationStatus(booking.estado, payment.estado));
          this.totalLoading.set(false);
          return;
        }

        this.calculateTotal(booking);
      },
      error: () => this.calculateTotal(booking),
    });
  }

  private calculateTotal(booking: BookingReservation): void {
    this.catalogService.calculateRoomPrice({
      id_categoria: booking.id_categoria,
      fecha_inicio: booking.fecha_check_in,
      fecha_fin: booking.fecha_check_out,
      pais_usuario: ReservationDetailPage.DEFAULT_USER_COUNTRY,
    }).subscribe({
      next: (price) => {
        this.updateDetailTotal(price.total, price.moneda, resolveReservationStatus(booking.estado, null));
        this.totalLoading.set(false);
      },
      error: () => {
        this.totalUnavailable.set(true);
        this.totalLoading.set(false);
      },
    });
  }

  private updateDetailTotal(amount: number, currency: string, status: ReservationStatus): void {
    const current = this.detail();
    if (!current) return;

    const cancellation = this.resolveCancellation(status, current.checkInDate, this.cancellationPolicyDays());

    this.detail.set({
      ...current,
      totalAmount: amount,
      currency,
      status,
      canCancel: cancellation.canCancel,
      cancellationReason: cancellation.reason,
    });
  }

  protected formatDate(dateStr: string): string {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }

  protected formatCurrency(amount: number | null, currency: string): string {
    if (amount === null) return '';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  protected getStatusLabel(status: ReservationStatus): string {
    return getStatusLabel(status);
  }

  protected getStatusClass(status: ReservationStatus): string {
    const map: Record<ReservationStatus, string> = {
      CONFIRMADA: 'status-badge--confirmada',
      PENDIENTE_PAGO: 'status-badge--pendiente-pago',
      PENDIENTE_CONFIRMACION_HOTEL: 'status-badge--pendiente-hotel',
      CANCELADA: 'status-badge--cancelada',
    };
    return map[status];
  }

  private getGuestCount(booking: BookingReservation): number {
    return (
      (booking.ocupacion?.adultos ?? 0) +
      (booking.ocupacion?.ninos ?? 0) +
      (booking.ocupacion?.infantes ?? 0)
    );
  }

  private isNotFoundError(error: unknown): boolean {
    if (error instanceof HttpErrorResponse) {
      return error.status === 404;
    }

    if (error instanceof Error) {
      return /\b404\b/.test(error.message);
    }

    return false;
  }
}
