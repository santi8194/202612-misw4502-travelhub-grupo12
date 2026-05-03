import { Component, inject } from '@angular/core';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { ReservationCardComponent } from '../../shared/components/reservation-card/reservation-card';
import { MyReservationsService } from '../../core/services/my-reservations';
import { ReservationFilter } from '../../models/reservation.interface';

@Component({
  selector: 'app-my-reservations-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, ReservationCardComponent],
  templateUrl: './my-reservations-page.html',
  styleUrl: './my-reservations-page.css',
})
export class MyReservationsPage {
  protected readonly service = inject(MyReservationsService);

  protected setFilter(filter: ReservationFilter): void {
    this.service.setFilter(filter);
  }
}
