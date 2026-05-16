import { Component, OnInit, inject } from '@angular/core';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { ReservationCardComponent } from '../../shared/components/reservation-card/reservation-card';
import { MyReservationsService } from '../../core/services/my-reservations';
import { ReservationFilter } from '../../models/reservation.interface';
import { TranslatePipe } from '../../shared/pipes/translate.pipe';

@Component({
  selector: 'app-my-reservations-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, ReservationCardComponent, TranslatePipe],
  templateUrl: './my-reservations-page.html',
  styleUrl: './my-reservations-page.css',
})
export class MyReservationsPage implements OnInit {
  protected readonly service = inject(MyReservationsService);

  ngOnInit(): void {
    this.service.loadCurrentUserReservations();
  }

  protected setFilter(filter: ReservationFilter): void {
    this.service.setFilter(filter);
  }
}
