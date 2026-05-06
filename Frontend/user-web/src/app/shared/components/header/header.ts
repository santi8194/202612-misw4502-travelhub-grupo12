import { Component, ElementRef, HostListener, computed, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Router } from '@angular/router';
import { SearchBarComponent } from '../search-bar/search-bar';
import { CompactSearchBarComponent } from '../compact-search-bar/compact-search-bar';
import { AuthService, UserProfile } from '../../../core/services/auth';
import { NotificationService } from '../../../core/services/notification';
import { BookingStore } from '../../../core/store/booking-store';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [SearchBarComponent, CompactSearchBarComponent, RouterLink],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class HeaderComponent {
  private readonly hostElement = inject(ElementRef<HTMLElement>);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly notificationService = inject(NotificationService);
  private readonly bookingStore = inject(BookingStore);

  mode = input<'default' | 'compact'>('default');
  profileMenuOpen = signal(false);
  userProfile = signal<UserProfile | null>(null);
  isLoadingProfile = signal(false);
  
  readonly userSession = computed(() => this.authService.session());
  readonly isAuthenticated = computed(() => !!this.userSession());

  constructor() {
    this.syncUserSession();
  }

  toggleProfileMenu(event?: Event): void {
    event?.stopPropagation();
    this.syncUserSession();
    
    if (!this.profileMenuOpen()) {
      this.loadUserProfile();
    }
    
    this.profileMenuOpen.update(open => !open);
  }

  closeProfileMenu(): void {
    this.profileMenuOpen.set(false);
  }

  logout(): void {
    this.authService.clearSession();
    this.userProfile.set(null);
    
    // Limpiar estado global de reservas
    if (typeof sessionStorage !== 'undefined') {
      // Limpiar todas las sesiones de reserva del sessionStorage
      const keysToRemove = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && (key.startsWith('booking-session:') || key.startsWith('hold:'))) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => sessionStorage.removeItem(key));
    }
    
    this.closeProfileMenu();
    this.notificationService.showSuccess('Tu sesión ha sido cerrada exitosamente.');
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
    }
  }

  private syncUserSession(): void {
    this.authService.getCurrentSession();
  }
}
