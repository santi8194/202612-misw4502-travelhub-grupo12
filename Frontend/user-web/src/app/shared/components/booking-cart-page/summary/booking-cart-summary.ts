import { Component, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BookingSummaryData } from '../../../../models/booking-summary.interface';
import { TranslatePipe } from '../../../../shared/pipes/translate.pipe';
import { CurrencyService } from '../../../../core/services/currency.service';

@Component({
  selector: 'app-booking-cart-summary',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './booking-cart-summary.html',
  styleUrl: './booking-cart-summary.css'
})
export class BookingCartSummaryComponent {
  protected readonly currency = inject(CurrencyService);
  @Input({ required: true }) data: BookingSummaryData | null = null;
  @Input() isLoading = false;

  formatPrice(value: number): string {
    const currency = this.data?.currency || 'COP';
    return this.currency.format(value, currency);
  }
}
