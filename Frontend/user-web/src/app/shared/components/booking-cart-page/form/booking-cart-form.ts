import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
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

  touched = signal({
    name: false,
    lastName: false,
    email: false,
    phone: false,
  });

  private readonly namePattern = /^[a-zA-ZáéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜñÑ\s'-]{1,50}$/;
  private readonly emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  private readonly phonePattern = /^\+57\d{10}$/;

  isFormValid(): boolean {
    const name = this.form.name.trim();
    const lastName = this.form.lastName.trim();
    const email = this.form.email.trim();
    const normalizedPhone = this.normalizePhone(this.form.phone);

    return !!name
      && !!lastName
      && !!email
      && !!normalizedPhone
      && this.namePattern.test(name)
      && this.namePattern.test(lastName)
      && this.emailPattern.test(email)
      && this.phonePattern.test(normalizedPhone);
  }

  onFieldChange(field: keyof GuestForm, value: string): void {
    this.fieldChange.emit({ field, value });
    this.validateField(field, value);
  }

  onFieldBlur(field: keyof GuestForm, value: string): void {
    this.touched.update(current => ({ ...current, [field]: true }));
    this.validateField(field, value);
  }

  shouldShowError(field: 'name' | 'lastName' | 'email' | 'phone'): boolean {
    const touched = this.touched();
    const errors = this.errors();
    return touched[field] && errors[field];
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
        isValid = !value.trim() ? false : this.phonePattern.test(this.normalizePhone(value));
        break;
    }

    this.errors.set({
      ...currentErrors,
      [field]: !isValid,
    });
  }

  onContinuePayment(): void {
    this.touched.set({
      name: true,
      lastName: true,
      email: true,
      phone: true,
    });

    this.validateField('name', this.form.name);
    this.validateField('lastName', this.form.lastName);
    this.validateField('email', this.form.email);
    this.validateField('phone', this.form.phone);

    if (this.disableContinue || !this.isFormValid()) {
      return;
    }
    this.continuePayment.emit();
  }

  private normalizePhone(phone: string): string {
    const compact = phone.replace(/[\s\-()]/g, '');
    if (!compact) {
      return compact;
    }

    return compact;
  }
}
