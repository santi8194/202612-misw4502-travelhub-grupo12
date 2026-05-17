import { Component, ElementRef, HostListener, computed, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Router } from '@angular/router';
import { catchError, finalize, of } from 'rxjs';
import { SearchBarComponent } from '../search-bar/search-bar';
import { CompactSearchBarComponent } from '../compact-search-bar/compact-search-bar';
import { AuthService, UserProfile } from '../../../core/services/auth';
import { NotificationService } from '../../../core/services/notification';
import { BookingStore } from '../../../core/store/booking-store';
import { BookingService } from '../../../core/services/booking';
import { I18nService, LanguageCode } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '../../pipes/translate.pipe';
import { CurrencyService, CurrencyCode } from '../../../core/services/currency.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [SearchBarComponent, CompactSearchBarComponent, RouterLink, TranslatePipe],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class HeaderComponent {
  private readonly hostElement = inject(ElementRef<HTMLElement>);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly notificationService = inject(NotificationService);
  private readonly bookingStore = inject(BookingStore);
  private readonly bookingService = inject(BookingService);
  protected readonly i18n = inject(I18nService);
  protected readonly currency = inject(CurrencyService);

  mode = input<'default' | 'compact'>('default');
  profileMenuOpen = signal(false);
  languageMenuOpen = signal(false);
  currencyMenuOpen = signal(false);
  userProfile = signal<UserProfile | null>(null);
  isLoadingProfile = signal(false);
  
  readonly userSession = computed(() => this.authService.session());
  readonly isAuthenticated = computed(() => !!this.userSession());
  readonly supportedLanguages = this.i18n.supportedLanguages;
  readonly supportedCurrencies = this.currency.supportedCurrencies;

  constructor() {
    this.syncUserSession();
  }

  toggleProfileMenu(event?: Event): void {
    event?.stopPropagation();
    this.syncUserSession();
    this.languageMenuOpen.set(false);
    this.currencyMenuOpen.set(false);
    
    if (!this.profileMenuOpen()) {
      this.loadUserProfile();
    }
    
    this.profileMenuOpen.update(open => !open);
  }

  closeProfileMenu(): void {
    this.profileMenuOpen.set(false);
  }

  toggleLanguageMenu(event?: Event): void {
    event?.stopPropagation();
    this.profileMenuOpen.set(false);
    this.currencyMenuOpen.set(false);
    this.languageMenuOpen.update(open => !open);
  }

  closeLanguageMenu(): void {
    this.languageMenuOpen.set(false);
  }

  toggleCurrencyMenu(event?: Event): void {
    event?.stopPropagation();
    this.profileMenuOpen.set(false);
    this.languageMenuOpen.set(false);
    this.currencyMenuOpen.update(open => !open);
  }

  closeCurrencyMenu(): void {
    this.currencyMenuOpen.set(false);
  }

  setActiveCurrency(code: CurrencyCode): void {
    this.currency.setCurrency(code);
    this.closeCurrencyMenu();
  }

  setLanguage(language: LanguageCode): void {
    this.i18n.setLanguage(language);
    this.closeLanguageMenu();
  }

  logout(): void {
    const reservationId = this.extractReservationId(this.router.url);

    const finishLogout = () => {
      this.authService.clearSession();
      this.userProfile.set(null);
      this.clearBookingStorage();
      this.closeProfileMenu();
      this.notificationService.showSuccess(this.i18n.translate('auth.login.logoutSuccess'));
      this.router.navigate(['/'], { replaceUrl: true });
    };

    if (!reservationId) {
      finishLogout();
      return;
    }

    this.bookingService
      .cancelBookingById(reservationId)
      .pipe(
        catchError((error) => {
          console.warn('[Header] No fue posible cancelar la reserva durante logout', {
            reservationId,
            error,
          });
          return of(null);
        }),
        finalize(finishLogout)
      )
      .subscribe();
  }

  goToMyReservations(): void {
    this.closeProfileMenu();
    this.router.navigate(['/mis-reservas']);
  }

  private loadUserProfile(): void {
    const session = this.userSession();
    console.log('[Header] loadUserProfile - session:', session);

    if (!session?.userId) {
      console.warn('[Header] No userId in session, skipping profile load');
      return;
    }

    if (this.userProfile() !== null) {
      console.log('[Header] Profile already loaded:', this.userProfile());
      return;
    }

    this.isLoadingProfile.set(true);
    console.log('[Header] Calling getUserProfile with userId:', session.userId);

    this.authService.getUserProfile(session.userId).subscribe({
      next: (profile) => {
        console.log('[Header] getUserProfile response:', profile);
        this.userProfile.set(profile);
        this.isLoadingProfile.set(false);
      },
      error: (err) => {
        console.error('[Header] getUserProfile error:', err);
        this.isLoadingProfile.set(false);
      }
    });
  }

  private getDisplayName(): string {
    const profile = this.userProfile();
    const session = this.userSession();
    console.log('[Header] getDisplayName - profile:', profile, 'session.userName:', session?.userName);

    if (profile?.full_name) {
      console.log('[Header] Using full_name:', profile.full_name);
      return profile.full_name;
    }

    console.log('[Header] Falling back to session.userName:', session?.userName);
    return session?.userName ?? 'Usuario';
  }

  getProfileDisplayName(): string {
    return this.getDisplayName();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as Node | null;
    if (target && !this.hostElement.nativeElement.contains(target)) {
      this.closeProfileMenu();
      this.closeLanguageMenu();
      this.closeCurrencyMenu();
    }
  }

  private syncUserSession(): void {
    this.authService.getCurrentSession();
  }

  private extractReservationId(url: string): string | null {
    const match = /^\/booking\/([^/?#]+)/.exec(url ?? '');
    return match?.[1] ?? null;
  }

  private clearBookingStorage(): void {
    if (typeof sessionStorage !== 'undefined') {
      const sessionKeysToRemove: string[] = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && (key.startsWith('booking-session:') || key.startsWith('hold:'))) {
          sessionKeysToRemove.push(key);
        }
      }
      sessionKeysToRemove.forEach((key) => sessionStorage.removeItem(key));
    }

    if (typeof localStorage !== 'undefined') {
      const localKeysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('booking-session:')) {
          localKeysToRemove.push(key);
        }
      }
      localKeysToRemove.forEach((key) => localStorage.removeItem(key));
    }
  }
}
