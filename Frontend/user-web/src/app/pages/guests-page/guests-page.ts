import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BookingService } from '../../core/services/booking';
import { BookingStore } from '../../core/store/booking-store';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';

@Component({
  selector: 'app-guests-page',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent, FooterComponent],
  templateUrl: './guests-page.html',
  styleUrl: './guests-page.css'
})
export class GuestsPage implements OnInit {

  private bookingService = inject(BookingService);
  private store = inject(BookingStore);

  form = {
    name: '',
    lastName: '',
    email: '',
    phone: '',
    detailedRequest: ''
  };

  remainingTime = 0;
  interval: any;

  ngOnInit() {
    this.loadHold();
  }

  async createHold() {
    try {
      const response = await this.bookingService.createHold({
        categoryId: 1,
        checkIn: '2026-10-10',
        checkOut: '2026-10-15',
        guests: 2
      });

      this.store.setHold(response);
      this.startTimer(response.expiresAt);

    } catch (e: any) {
      alert('No hay cupos disponibles');
    }
  }

  loadHold() {
    const hold = this.store.getHold();

    if (hold) {
      this.startTimer(hold.expiresAt);
    }
  }

  startTimer(expiresAt: number) {
    this.interval = setInterval(() => {
      const diff = Math.floor((expiresAt - Date.now()) / 1000);

      if (diff <= 0) {
        clearInterval(this.interval);
        this.remainingTime = 0;
        this.store.clear();
        alert('El hold expiró');
      } else {
        this.remainingTime = diff;
      }
    }, 1000);
  }
}