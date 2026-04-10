import { Component, OnDestroy, computed, inject, signal } from '@angular/core';
import { BookingService } from '../../core/services/booking';
import { BookingStore } from '../../core/store/booking-store';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { BookingCartFormComponent } from '../../shared/components/booking-cart-page/form/booking-cart-form';
import { BookingCartSummaryComponent } from '../../shared/components/booking-cart-page/summary/booking-cart-summary';
import { BookingCartStepperComponent } from '../../shared/components/booking-cart-page/stepper/booking-cart-stepper';
import { GuestForm } from '../../models/guest.interface';
import { HoldRequest } from '../../models/hold.interface';

@Component({
  selector: 'app-booking-cart-page',
  imports: [
    HeaderComponent,
    FooterComponent,
    BookingCartStepperComponent,
    BookingCartFormComponent,
    BookingCartSummaryComponent,
  ],
  templateUrl: './booking-cart-page.html',
  styleUrl: './booking-cart-page.css'
})
export class BookingCartPage implements OnDestroy {
  private readonly bookingService = inject(BookingService);
  private readonly store = inject(BookingStore);

  form = signal<GuestForm>({
    name: '',
    lastName: '',
    email: '',
    phone: '',
    detailedRequest: ''
  });

  remainingTime = signal(0);
  timerActive = computed(() => this.remainingTime() > 0);

  updateField(field: keyof GuestForm, value: string): void {
    this.form.update(current => ({ ...current, [field]: value }));
  }

  onFieldChange(event: { field: keyof GuestForm; value: string }): void {
    this.updateField(event.field, event.value);
  }

  private intervalId: ReturnType<typeof setInterval> | null = null;

  constructor() {
    this.loadHold();
  }

  createHold(): void {
    const request: HoldRequest = {
      categoryId: 1,
      checkIn: '2026-10-10',
      checkOut: '2026-10-15',
      guests: 2
    };

    this.bookingService.createHold(request).subscribe({
      next: (response) => {
        this.store.setHold(response);
        this.startTimer(response.expiresAt);
      },
      error: () => {
        alert('No hay cupos disponibles');
      }
    });
  }

  private loadHold(): void {
    const hold = this.store.getHold();
    if (hold) {
      this.startTimer(hold.expiresAt);
    }
  }

  private startTimer(expiresAt: number): void {
    this.clearTimer();
    this.intervalId = setInterval(() => {
      const diff = Math.floor((expiresAt - Date.now()) / 1000);

      if (diff <= 0) {
        this.clearTimer();
        this.remainingTime.set(0);
        this.store.clear();
        alert('El hold expiró');
      } else {
        this.remainingTime.set(diff);
      }
    }, 1000);
  }

  private clearTimer(): void {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  ngOnDestroy(): void {
    this.clearTimer();
  }
}
