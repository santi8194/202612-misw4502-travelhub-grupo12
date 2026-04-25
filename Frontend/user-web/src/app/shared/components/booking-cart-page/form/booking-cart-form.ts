import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { GuestForm } from '../../../../models/guest.interface';

@Component({
  selector: 'app-booking-cart-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './booking-cart-form.html',
  styleUrl: './booking-cart-form.css'
})
export class BookingCartFormComponent {
  @Input({ required: true }) form!: GuestForm;
  @Input() disableContinue = false;
  @Input() isSubmitting = false;

  @Output() fieldChange = new EventEmitter<{ field: keyof GuestForm; value: string }>();
  @Output() continuePayment = new EventEmitter<void>();

  onFieldChange(field: keyof GuestForm, value: string): void {
    this.fieldChange.emit({ field, value });
  }

  onContinuePayment(): void {
    if (this.disableContinue) {
      return;
    }
    this.continuePayment.emit();
  }
}
