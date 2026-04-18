import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService, UserProfile } from '../../core/services/auth.service';
import { Subject, takeUntil } from 'rxjs';
import { PreciosPorHabitacionComponent } from './components/precios-por-habitacion/precios-por-habitacion.component';

@Component({
    selector: 'app-home',
    standalone: true,
    imports: [CommonModule, PreciosPorHabitacionComponent],
    templateUrl: './home.component.html',
    styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit, OnDestroy {
    user: UserProfile | null = null;
    loading = true;
    error = false;
    activeSection = 'dashboard';
    readonly todayLabel = new Date();
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
    readonly pricingSummaryCards = [
        {
            icon: '$',
            value: '$215',
            label: 'Tarifa promedio',
            trend: '↗',
            trendText: '',
            iconClass: 'pricing-icon-money',
            trendClass: 'trend-positive'
        },
        {
            icon: '▦',
            value: '3',
            label: 'Promociones',
            trend: '',
            trendText: 'Activas',
            iconClass: 'pricing-icon-calendar',
            trendClass: 'trend-neutral'
        },
        {
            icon: '↗',
            value: '$18.5K',
            label: 'Ingresos este mes',
            trend: '',
            trendText: '+12%',
            iconClass: 'pricing-icon-revenue',
            trendClass: 'trend-positive'
        }
    ];
    readonly preciosPorHabitacionComponent = PreciosPorHabitacionComponent;
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

    setActiveSection(section: string): void {
        this.activeSection = section;
    }

    isDashboardSelected(): boolean {
        return this.activeSection === 'dashboard';
    }

    isPricingSelected(): boolean {
        return this.activeSection === 'precios';
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }
}
