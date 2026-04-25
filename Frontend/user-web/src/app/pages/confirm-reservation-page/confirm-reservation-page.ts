import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';

@Component({
  selector: 'app-confirm-reservation-page',
  standalone: true,
  imports: [RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './confirm-reservation-page.html',
  styleUrl: './confirm-reservation-page.css',
})
export class ConfirmReservationPage {
  private readonly route = inject(ActivatedRoute);

  readonly reservationId = computed(() => this.route.snapshot.paramMap.get('id_reserva') ?? 'N/A');
  readonly status = computed(() => this.route.snapshot.queryParamMap.get('status') ?? 'rejected');
  readonly reason = computed(
    () =>
      this.route.snapshot.queryParamMap.get('reason')
      ?? (this.isConfirmed()
        ? 'Tu reserva fue confirmada y está en proceso de coordinación con hoteles y pagos.'
        : 'No fue posible confirmar la reserva en este momento.')
  );

  readonly isConfirmed = computed(() => this.status() === 'confirmed');
  readonly title = computed(() => this.isConfirmed() ? 'Reserva confirmada' : 'Reserva no confirmada');
}