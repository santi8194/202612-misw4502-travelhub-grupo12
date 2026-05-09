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
  readonly showPasswordRequirements = signal(false);

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

  errorMessages = signal({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });

  private touched = signal({
    firstName: false,
    lastName: false,
    email: false,
    phone: false,
    password: false,
    confirmPassword: false,
  });

  private readonly namePattern = /^[a-zA-ZáéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜñÑ\s'-]{1,50}$/;
  private readonly passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$/;

  hasMinPasswordLength(): boolean {
    return this.form().password.length >= 8;
  }

  hasPasswordLowercase(): boolean {
    return /[a-z]/.test(this.form().password);
  }

  hasPasswordUppercase(): boolean {
    return /[A-Z]/.test(this.form().password);
  }

  hasPasswordNumber(): boolean {
    return /\d/.test(this.form().password);
  }

  hasPasswordSpecialChar(): boolean {
    return /[^A-Za-z0-9]/.test(this.form().password);
  }

  togglePassword(): void {
    this.showPassword.update(value => !value);
  }

  toggleConfirmPassword(): void {
    this.showConfirmPassword.update(value => !value);
  }

  togglePasswordRequirements(): void {
    this.showPasswordRequirements.update(value => !value);
  }

  onGoogleSignUp(): void {
    alert('El registro con Google no está disponible en este momento. Por favor, usa el formulario de registro.');
  }

  updateField(
    field: 'firstName' | 'lastName' | 'email' | 'phone' | 'password' | 'confirmPassword',
    value: string
  ): void {
    this.form.update(current => ({ ...current, [field]: value }));
    if (this.touched()[field]) {
      this.validateSingleField(field, value);
    }
  }

  markTouched(field: 'firstName' | 'lastName' | 'email' | 'phone' | 'password' | 'confirmPassword'): void {
    this.touched.update(t => ({ ...t, [field]: true }));
    this.validateSingleField(field, this.form()[field]);
  }

  private validateSingleField(
    field: 'firstName' | 'lastName' | 'email' | 'phone' | 'password' | 'confirmPassword',
    value: string
  ): void {
    let hasError = false;
    let message = '';

    switch (field) {
      case 'firstName':
        if (!value.trim()) { hasError = true; message = 'El nombre es obligatorio.'; }
        else if (!this.namePattern.test(value.trim())) { hasError = true; message = 'Solo letras, espacios y guiones (máx. 50 caracteres).'; }
        break;
      case 'lastName':
        if (!value.trim()) { hasError = true; message = 'El apellido es obligatorio.'; }
        else if (!this.namePattern.test(value.trim())) { hasError = true; message = 'Solo letras, espacios y guiones (máx. 50 caracteres).'; }
        break;
      case 'email':
        if (!value.trim()) { hasError = true; message = 'El correo es obligatorio.'; }
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) { hasError = true; message = 'Ingresa un correo válido (ej: tu@ejemplo.com).'; }
        break;
      case 'phone':
        if (!value.trim()) { hasError = true; message = 'El teléfono es obligatorio.'; }
        else if (!/^\+[1-9]\d{6,14}$/.test(value.replace(/[\s\-()]/g, ''))) {
          hasError = true; message = 'Debe incluir el código de país (ej: +573001112233).';
        }
        break;
      case 'password':
        if (!value) { hasError = true; message = 'La contraseña es obligatoria.'; }
        else if (!this.passwordPattern.test(value)) {
          hasError = true; message = 'Debe tener mínimo 8 caracteres, una mayúscula, una minúscula, un número y un símbolo.';
        }
        break;
      case 'confirmPassword': {
        const currentPassword = this.form().password;
        if (!value) { hasError = true; message = 'Confirma tu contraseña.'; }
        else if (value !== currentPassword) { hasError = true; message = 'Las contraseñas no coinciden.'; }
        break;
      }
    }

    this.errors.update(e => ({
      ...e,
      [field]: hasError,
      passwordMismatch: field === 'confirmPassword' ? (hasError && value !== this.form().password) : e.passwordMismatch,
    }));
    this.errorMessages.update(m => ({ ...m, [field]: message }));
  }

  private validateForm(): boolean {
    const f = this.form();
    this.touched.set({ firstName: true, lastName: true, email: true, phone: true, password: true, confirmPassword: true });

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email.trim());
    const phoneValid = !!f.phone.trim() && /^\+[1-9]\d{6,14}$/.test(f.phone.replace(/[\s\-()]/g, ''));
    const passwordValid = this.passwordPattern.test(f.password);
    const firstNameValid = !!f.firstName.trim() && this.namePattern.test(f.firstName.trim());
    const lastNameValid = !!f.lastName.trim() && this.namePattern.test(f.lastName.trim());
    const confirmPasswordValid = !!f.confirmPassword && f.confirmPassword === f.password;

    const nextErrors = {
      firstName: !firstNameValid,
      lastName: !lastNameValid,
      email: !emailValid,
      phone: !phoneValid,
      password: !passwordValid,
      confirmPassword: !confirmPasswordValid,
      passwordMismatch: !!f.password && !!f.confirmPassword && f.password !== f.confirmPassword,
    };

    this.errors.set(nextErrors);
    this.errorMessages.set({
      firstName: !f.firstName.trim() ? 'El nombre es obligatorio.' : !this.namePattern.test(f.firstName.trim()) ? 'Solo letras, espacios y guiones (máx. 50 caracteres).' : '',
      lastName: !f.lastName.trim() ? 'El apellido es obligatorio.' : !this.namePattern.test(f.lastName.trim()) ? 'Solo letras, espacios y guiones (máx. 50 caracteres).' : '',
      email: !f.email.trim() ? 'El correo es obligatorio.' : !emailValid ? 'Ingresa un correo válido (ej: tu@ejemplo.com).' : '',
      phone: !f.phone.trim() ? 'El teléfono es obligatorio.' : !phoneValid ? 'Debe incluir el código de país (ej: +573001112233).' : '',
      password: !f.password ? 'La contraseña es obligatoria.' : !passwordValid ? 'Debe tener mínimo 8 caracteres, una mayúscula, una minúscula, un número y un símbolo.' : '',
      confirmPassword: !f.confirmPassword ? 'Confirma tu contraseña.' : f.confirmPassword !== f.password ? 'Las contraseñas no coinciden.' : '',
    });

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