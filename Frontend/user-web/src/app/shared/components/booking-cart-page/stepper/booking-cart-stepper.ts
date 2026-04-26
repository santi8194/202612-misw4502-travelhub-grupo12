import { Component, Input } from '@angular/core';

type StepperVariant = 'cart' | 'confirmed' | 'rejected';

@Component({
  selector: 'app-booking-cart-stepper',
  standalone: true,
  templateUrl: './booking-cart-stepper.html',
  styleUrl: './booking-cart-stepper.css'
})
export class BookingCartStepperComponent {
  @Input() variant: StepperVariant = 'cart';

  isCart(): boolean {
    return this.variant === 'cart';
  }

  isConfirmed(): boolean {
    return this.variant === 'confirmed';
  }

  isRejected(): boolean {
    return this.variant === 'rejected';
  }

  isResult(): boolean {
    return this.variant === 'confirmed' || this.variant === 'rejected';
  }
}
