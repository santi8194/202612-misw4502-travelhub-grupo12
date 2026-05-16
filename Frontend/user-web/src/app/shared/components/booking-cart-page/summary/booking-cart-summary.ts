import { Component, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BookingSummaryData } from '../../../../models/booking-summary.interface';
import { I18nService } from '../../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../../../shared/pipes/translate.pipe';

@Component({
  selector: 'app-booking-cart-summary',
  standalone: true,
  imports: [CommonModule, TranslatePipe],
  templateUrl: './booking-cart-summary.html',
  styleUrl: './booking-cart-summary.css'
})
export class BookingCartSummaryComponent {
  private readonly i18n = inject(I18nService);
  @Input({ required: true }) data: BookingSummaryData | null = null;
  @Input() isLoading = false;

  formatPrice(value: number): string {
    const currency = this.data?.currency || 'COP';
    return this.i18n.formatCurrency(value, currency);
  }
}
