import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';

import { AuthService } from '../../core/services/auth';
import { NotificationService } from '../../core/services/notification';
import { I18nService } from '../../core/i18n/i18n.service';
import { TranslatePipe } from '../../shared/pipes/translate.pipe';

@Component({
  selector: 'app-auth-login-page',
  standalone: true,
  imports: [FormsModule, RouterLink, HeaderComponent, FooterComponent, TranslatePipe],
  templateUrl: './auth-login-page.html',
  styleUrl: './auth-login-page.css',
})
export class AuthLoginPage {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly i18n = inject(I18nService);
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

  errorMessages = signal({
    email: '',
    password: '',
  });

  private touched = signal({
    email: false,
    password: false,
  });

  togglePassword(): void {
    this.showPassword.update(value => !value);
  }

  onGoogleSignIn(): void {
    alert(this.i18n.translate('auth.login.googleUnavailable'));
  }

  onRememberMe(): void {
    alert(this.i18n.translate('auth.login.rememberUnavailable'));
  }

  onForgotPassword(): void {
    alert(this.i18n.translate('auth.login.forgotUnavailable'));
  }

  updateField(field: 'email' | 'password', value: string): void {
    this.form.update(current => ({ ...current, [field]: value }));
    if (this.touched()[field]) {
      this.validateSingleField(field, value);
    }
  }

  markTouched(field: 'email' | 'password'): void {
    this.touched.update(t => ({ ...t, [field]: true }));
    this.validateSingleField(field, this.form()[field]);
  }

  private validateSingleField(field: 'email' | 'password', value: string): void {
    let hasError = false;
    let message = '';

    if (field === 'email') {
      if (!value.trim()) {
        hasError = true;
          message = this.i18n.translate('auth.login.emailRequired');
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) {
        hasError = true;
          message = this.i18n.translate('auth.login.emailInvalid');
      }
    } else if (field === 'password') {
      if (!value.trim()) {
        hasError = true;
          message = this.i18n.translate('auth.login.passwordRequired');
      }
    }

    this.errors.update(e => ({ ...e, [field]: hasError }));
    this.errorMessages.update(m => ({ ...m, [field]: message }));
  }

  private validateForm(): boolean {
    const f = this.form();
    this.touched.set({ email: true, password: true });

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email.trim());
    const passwordValid = !!f.password.trim();

    const nextErrors = {
      email: !emailValid,
      password: !passwordValid,
    };

    this.errors.set(nextErrors);
    this.errorMessages.set({
      email: !emailValid ? (!f.email.trim() ? this.i18n.translate('auth.login.emailRequired') : this.i18n.translate('auth.login.emailInvalid')) : '',
      password: !passwordValid ? this.i18n.translate('auth.login.passwordRequired') : '',
    });

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
            this.i18n.translate('auth.login.success')
          );

          this.router.navigateByUrl(redirectTarget);
        },

        error: () => {
          this.notificationService.showError(
            this.i18n.translate('auth.login.error')
          );

          this.loading.set(false);
        },

        complete: () => {
          this.loading.set(false);
        },
      });
  }
}