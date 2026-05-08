import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';

import { AuthService } from '../../core/services/auth';
import { NotificationService } from '../../core/services/notification';

@Component({
  selector: 'app-auth-register-page',
  standalone: true,
  imports: [FormsModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './auth-register-page.html',
  styleUrl: './auth-register-page.css',
})
export class AuthRegisterPage {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly router = inject(Router);

  readonly loading = signal(false);

  readonly showPassword = signal(false);
  readonly showConfirmPassword = signal(false);

  form = signal({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });

  errors = signal({
    firstName: false,
    lastName: false,
    email: false,
    phone: false,
    password: false,
    confirmPassword: false,
    passwordMismatch: false,
  });

  togglePassword(): void {
    this.showPassword.update(value => !value);
  }

  toggleConfirmPassword(): void {
    this.showConfirmPassword.update(value => !value);
  }

  updateField(
    field:
      | 'firstName'
      | 'lastName'
      | 'email'
      | 'phone'
      | 'password'
      | 'confirmPassword',
    value: string
  ): void {
    this.form.update(current => ({
      ...current,
      [field]: value,
    }));

    this.errors.update(current => ({
      ...current,
      [field]: false,
      passwordMismatch: false,
    }));
  }

  private validateForm(): boolean {
    const f = this.form();

    const passwordPattern =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$/;

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      f.email.trim()
    );

    const phoneValid =
      !f.phone.trim() ||
      /^\+[1-9]\d{7,14}$/.test(
        f.phone.replace(/\s/g, '')
      );

    const passwordValid = passwordPattern.test(f.password);

    const nextErrors = {
      firstName: !f.firstName.trim(),
      lastName: !f.lastName.trim(),
      email: !emailValid,
      phone: !phoneValid,
      password: !passwordValid,
      confirmPassword: !f.confirmPassword,
      passwordMismatch:
        !!f.password &&
        !!f.confirmPassword &&
        f.password !== f.confirmPassword,
    };

    this.errors.set(nextErrors);

    return !Object.values(nextErrors).some(Boolean);
  }

  onSubmit(): void {
    if (!this.validateForm() || this.loading()) {
      return;
    }

    this.loading.set(true);

    const f = this.form();

    this.authService
      .register({
        email: f.email.trim(),
        password: f.password,
        first_name: f.firstName.trim(),
        last_name: f.lastName.trim(),
        phone_number: f.phone.trim(),
      })
      .subscribe({
        next: () => {
          this.notificationService.showSuccess(
            'Te enviamos un código de verificación. Revisa tu correo para confirmar tu cuenta.'
          );

          this.router.navigate(['/auth/confirmar'], {
            queryParams: {
              email: f.email.trim(),
            },
          });
        },

        error: () => {
          this.notificationService.showError(
            'No fue posible registrar la cuenta. Verifica los datos e intenta nuevamente.'
          );

          this.loading.set(false);
        },

        complete: () => {
          this.loading.set(false);
        },
      });
  }
}