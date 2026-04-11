import { Component, OnDestroy, OnInit } from '@angular/core';
import { NavbarComponent } from '../../shared/components/navbar/navbar.component';
import { CommonModule } from '@angular/common';
import { AuthService, UserProfile } from '../../core/services/auth.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
    selector: 'app-home',
    standalone: true,
    imports: [NavbarComponent, CommonModule],
    templateUrl: './home.component.html',
    styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
    user: UserProfile | null = null;
    loading = true;
    error = false;
    showSessionInfo = true;
    showLockoutInfo = true;
    sessionExpirationAt: Date | null = null;
    readonly sessionInfo: {
        accessTokenMinutes: number;
        idleTimeoutMinutes: number;
        refreshTokenDays: number;
    };
    readonly lockoutPolicyInfo = {
        maxFailedAttempts: 5,
        lockoutMinutes: 5,
    };
    private destroy$ = new Subject<void>();

    constructor(private authService: AuthService) {
        this.sessionInfo = {
            accessTokenMinutes: this.authService.accessTokenMinutes,
            idleTimeoutMinutes: this.authService.idleTimeoutMinutes,
            refreshTokenDays: this.authService.refreshTokenDays,
        };
    }

    ngOnInit(): void {
        this.sessionExpirationAt = this.authService.getSessionExpiry();
        this.authService.sessionExpiry$
            .pipe(takeUntil(this.destroy$))
            .subscribe((expirationAt) => {
                this.sessionExpirationAt = expirationAt;
            });

        this.authService.getCurrentUser().subscribe({
            next: (profile) => {
                this.user = profile;
                this.loading = false;
            },
            error: () => {
                this.error = true;
                this.loading = false;
            }
        });
    }

    dismissSessionInfo(): void {
        this.showSessionInfo = false;
    }

    dismissLockoutInfo(): void {
        this.showLockoutInfo = false;
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }
}
