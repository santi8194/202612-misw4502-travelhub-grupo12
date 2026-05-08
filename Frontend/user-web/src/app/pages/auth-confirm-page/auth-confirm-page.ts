import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { AuthService } from '../../core/services/auth';
import { NotificationService } from '../../core/services/notification';

@Component({
  selector: 'app-auth-confirm-page',
  standalone: true,
  imports: [FormsModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './auth-confirm-page.html',
  styleUrl: './auth-confirm-page.css',
})
export class AuthConfirmPage {
  private readonly authService = inject(AuthService);
  private readonly notificationService = inject(NotificationService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly loading = signal(false);

  form = signal({
    email: this.route.snapshot.queryParamMap.get('email') ?? '',
    code: '',
  });

  errors = signal({
    email: false,
    code: false,
  });

  updateField(field: 'email' | 'code', value: string): void {
    this.form.update(current => ({ ...current, [field]: value }));
    this.errors.update(current => ({ ...current, [field]: false }));
  }

  private validateForm(): boolean {
    const f = this.form();
    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email.trim());
    const codeValid = /^\d{6}$/.test(f.code.trim());

    const nextErrors = {
      email: !emailValid,
      code: !codeValid,
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
      .confirmRegistration({
        email: f.email.trim(),
        code: f.code.trim(),
      })
      .subscribe({
        next: () => {
          this.notificationService.showSuccess('Correo confirmado. Ahora puedes iniciar sesión.');
          this.router.navigate(['/auth/login'], { queryParams: { email: f.email.trim() } });
        },
        error: () => {
          this.notificationService.showError(
            'No se pudo confirmar el código. Verifica e intenta nuevamente.'
          );
          this.loading.set(false);
        },
        complete: () => this.loading.set(false),
      });
  }
}
