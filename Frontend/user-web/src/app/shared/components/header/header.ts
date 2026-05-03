import { Component, ElementRef, HostListener, computed, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { SearchBarComponent } from '../search-bar/search-bar';
import { CompactSearchBarComponent } from '../compact-search-bar/compact-search-bar';
import { AuthService } from '../../../core/services/auth';

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

  mode = input<'default' | 'compact'>('default');
  profileMenuOpen = signal(false);
  readonly userSession = computed(() => this.authService.session());
  readonly isAuthenticated = computed(() => !!this.userSession());

  constructor() {
    this.syncUserSession();
  }

  toggleProfileMenu(event?: Event): void {
    event?.stopPropagation();
    this.syncUserSession();
    this.profileMenuOpen.update(open => !open);
  }

  closeProfileMenu(): void {
    this.profileMenuOpen.set(false);
  }

  logout(): void {
    this.authService.clearSession();
    this.closeProfileMenu();
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
