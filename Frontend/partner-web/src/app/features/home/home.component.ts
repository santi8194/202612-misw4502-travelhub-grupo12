import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService, UserProfile } from '../../core/services/auth.service';
import { Subject, takeUntil } from 'rxjs';
import { PreciosPorHabitacionComponent } from './components/precios-por-habitacion/precios-por-habitacion.component';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
    selector: 'app-home',
    standalone: true,
    imports: [CommonModule, TranslateModule],
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
    showLangSelector = false;
    readonly availableLanguages = [
        { code: 'en', label: 'English (EN)' },
        { code: 'es', label: 'Español (ES)' },
        { code: 'fr', label: 'Français (FR)' },
        { code: 'pt', label: 'Português (PT)' }
    ];
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
    readonly sectionKeys: Record<string, { titleKey: string; subtitleKey: string }> = {
        dashboard: {
            titleKey: 'SECTIONS.DASHBOARD_TITLE',
            subtitleKey: 'SECTIONS.DASHBOARD_SUBTITLE'
        },
        reservas: {
            titleKey: 'SECTIONS.RESERVATIONS_TITLE',
            subtitleKey: 'SECTIONS.RESERVATIONS_SUBTITLE'
        },
        inventario: {
            titleKey: 'SECTIONS.INVENTORY_TITLE',
            subtitleKey: 'SECTIONS.INVENTORY_SUBTITLE'
        },
        precios: {
            titleKey: 'SECTIONS.PRICING_TITLE',
            subtitleKey: 'SECTIONS.PRICING_SUBTITLE'
        },
        reportes: {
            titleKey: 'SECTIONS.REPORTS_TITLE',
            subtitleKey: 'SECTIONS.REPORTS_SUBTITLE'
        }
    };
    readonly pricingSummaryCards = [
        {
            icon: '$',
            value: '$215',
            labelKey: 'PRICING_CARDS.AVG_RATE',
            trend: '↗',
            trendText: '',
            iconClass: 'pricing-icon-money',
            trendClass: 'trend-positive'
        },
        {
            icon: '▦',
            value: '3',
            labelKey: 'PRICING_CARDS.PROMOTIONS',
            trend: '',
            trendTextKey: 'PRICING_CARDS.ACTIVE',
            iconClass: 'pricing-icon-calendar',
            trendClass: 'trend-neutral'
        },
        {
            icon: '↗',
            value: '$18.5K',
            labelKey: 'PRICING_CARDS.MONTHLY_REVENUE',
            trend: '',
            trendText: '+12%',
            iconClass: 'pricing-icon-revenue',
            trendClass: 'trend-positive'
        }
    ];
    readonly preciosPorHabitacionComponent = PreciosPorHabitacionComponent;
    private destroy$ = new Subject<void>();

    constructor(private authService: AuthService, public translate: TranslateService, private router: Router) {
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

    get currentSectionTitleKey(): string {
        return this.sectionKeys[this.activeSection]?.titleKey ?? 'SECTIONS.DASHBOARD_TITLE';
    }

    get currentSectionSubtitleKey(): string {
        return this.sectionKeys[this.activeSection]?.subtitleKey ?? 'SECTIONS.DASHBOARD_SUBTITLE';
    }

    guardarCambiosPrecios(): void {
        // Placeholder de UI para mock; la persistencia se conectara en siguiente paso.
    }

    get currentLangLabel(): string {
        const code = this.translate.currentLang || 'es';
        return this.availableLanguages.find(l => l.code === code)?.label ?? code;
    }

    toggleLangSelector(): void {
        this.showLangSelector = !this.showLangSelector;
    }

    switchLang(code: string): void {
        this.translate.use(code);
        this.showLangSelector = false;
    }

    logout(): void {
        this.authService.logout();
        this.router.navigate(['/login']);
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }
}
