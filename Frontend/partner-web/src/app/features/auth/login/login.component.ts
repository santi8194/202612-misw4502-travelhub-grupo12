import { Component, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { NgIf } from '@angular/common';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
    selector: 'app-login',
    imports: [ReactiveFormsModule, RouterLink, NgIf, TranslateModule],
    templateUrl: './login.component.html',
    styleUrl: './login.component.scss'
})
export class LoginComponent implements OnDestroy {
    loginForm: FormGroup;
    isLoading = false;
    errorMessage = '';
    private destroy$ = new Subject<void>();

    constructor(
        private fb: FormBuilder,
        private authService: AuthService,
        private router: Router,
        private translate: TranslateService
    ) {
        this.loginForm = this.fb.group({
            email: ['', [Validators.required, Validators.email]],
            password: ['', Validators.required],
            rememberMe: [false]
        });
    }

    onSubmit() {
        if (this.loginForm.valid) {
            this.isLoading = true;
            this.errorMessage = '';

            const { email, password } = this.loginForm.value;

            this.authService.login({ email, password })
                .pipe(takeUntil(this.destroy$))
                .subscribe({
                    next: () => {
                        this.isLoading = false;
                        this.router.navigate(['/']);
                    },
                    error: (err) => {
                        this.isLoading = false;
                        this.errorMessage = err?.error?.detail || this.translate.instant('LOGIN.ERROR_FALLBACK');
                    }
                });
        }
    }

    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete();
    }
}
