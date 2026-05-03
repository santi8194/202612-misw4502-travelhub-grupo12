import { Component, inject, input, signal } from '@angular/core';
import { Router } from '@angular/router';
import { SearchBarComponent } from '../search-bar/search-bar';
import { CompactSearchBarComponent } from '../compact-search-bar/compact-search-bar';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [SearchBarComponent, CompactSearchBarComponent],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class HeaderComponent {
  mode = input<'default' | 'compact'>('default');

  protected readonly isMenuOpen = signal(false);
  private readonly router = inject(Router);

  protected toggleMenu(): void {
    this.isMenuOpen.update(v => !v);
  }

  protected closeMenu(): void {
    this.isMenuOpen.set(false);
  }

  protected navigateTo(path: string): void {
    this.closeMenu();
    this.router.navigate([path]);
  }
}
