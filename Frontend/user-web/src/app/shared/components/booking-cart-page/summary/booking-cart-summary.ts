import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BookingSummaryData } from '../../../../models/booking-summary.interface';

@Component({
  selector: 'app-booking-cart-summary',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './booking-cart-summary.html',
  styleUrl: './booking-cart-summary.css'
})
export class BookingCartSummaryComponent {
  @Input({ required: true }) data: BookingSummaryData | null = null;
  @Input() isLoading = false;
}
