import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';

import { AuthService } from '../../core/services/auth';
import { NotificationService } from '../../core/services/notification';

@Component({
  selector: 'app-auth-login-page',
  standalone: true,
  imports: [FormsModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './auth-login-page.html',
  styleUrl: './auth-login-page.css',
})
export class AuthLoginPage {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly loading = signal(false);
  readonly showPassword = signal(false);

  form = signal({
    email: this.route.snapshot.queryParamMap.get('email') ?? '',
    password: '',
  });

  errors = signal({
    email: false,
    password: false,
  });

  togglePassword(): void {
    this.showPassword.update(value => !value);
  }

  updateField(field: 'email' | 'password', value: string): void {
    this.form.update(current => ({
      ...current,
      [field]: value,
    }));

    this.errors.update(current => ({
      ...current,
      [field]: false,
    }));
  }

  private validateForm(): boolean {
    const f = this.form();

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      f.email.trim()
    );

    const passwordValid = !!f.password.trim();

    const nextErrors = {
      email: !emailValid,
      password: !passwordValid,
    };

    this.errors.set(nextErrors);

    return !Object.values(nextErrors).some(Boolean);
  }

  onSubmit(): void {
    if (!this.validateForm() || this.loading()) {
      return;
    }

    const f = this.form();

    this.loading.set(true);

    this.authService
      .login({
        email: f.email.trim(),
        password: f.password,
      })
      .subscribe({
        next: response => {
          const redirectTarget =
            this.route.snapshot.queryParamMap.get('redirect') || '/';

          this.authService.saveSession(response, f.email.trim());

          this.notificationService.showSuccess(
            'Inicio de sesión exitoso. Bienvenido a TravelHub.'
          );

          this.router.navigateByUrl(redirectTarget);
        },

        error: () => {
          this.notificationService.showError(
            'No se pudo iniciar sesión. Verifica tus credenciales e intenta nuevamente.'
          );

          this.loading.set(false);
        },

        complete: () => {
          this.loading.set(false);
        },
      });
  }
}