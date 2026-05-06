import { Component, EventEmitter, Input, Output, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { GuestForm } from '../../../../models/guest.interface';

@Component({
  selector: 'app-booking-cart-form',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './booking-cart-form.html',
  styleUrl: './booking-cart-form.css'
})
export class BookingCartFormComponent {
  @Input({ required: true }) form!: GuestForm;
  @Input() disableContinue = false;
  @Input() isSubmitting = false;

  @Output() fieldChange = new EventEmitter<{ field: keyof GuestForm; value: string }>();
  @Output() continuePayment = new EventEmitter<void>();

  errors = signal({
    name: false,
    lastName: false,
    email: false,
    phone: false,
  });

  private readonly namePattern = /^[a-zA-ZáéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜñÑ\s'-]{1,50}$/;
  private readonly emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  private readonly phonePattern = /^[\+]?[0-9\s\-()]{10,}$/;

  readonly formValid = computed(() => {
    const e = this.errors();
    return !Object.values(e).some(Boolean) &&
      this.form.name.trim() &&
      this.form.lastName.trim() &&
      this.form.email.trim() &&
      this.form.phone.trim();
  });

  onFieldChange(field: keyof GuestForm, value: string): void {
    this.fieldChange.emit({ field, value });
    this.validateField(field, value);
  }

  private validateField(field: keyof GuestForm, value: string): void {
    const currentErrors = this.errors();
    let isValid = true;

    switch (field) {
      case 'name':
        isValid = !value.trim() ? false : this.namePattern.test(value.trim());
        break;
      case 'lastName':
        isValid = !value.trim() ? false : this.namePattern.test(value.trim());
        break;
      case 'email':
        isValid = !value.trim() ? false : this.emailPattern.test(value.trim());
        break;
      case 'phone':
        isValid = !value.trim() ? false : this.phonePattern.test(value.replace(/\s/g, ''));
        break;
    }

    this.errors.set({
      ...currentErrors,
      [field]: !isValid,
    });
  }

  onContinuePayment(): void {
    if (this.disableContinue || !this.formValid()) {
      return;
    }
    this.continuePayment.emit();
  }
}
