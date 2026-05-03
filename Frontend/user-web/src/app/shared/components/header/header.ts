import { Component, ElementRef, HostListener, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { SearchBarComponent } from '../search-bar/search-bar';
import { CompactSearchBarComponent } from '../compact-search-bar/compact-search-bar';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [SearchBarComponent, CompactSearchBarComponent, RouterLink],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class HeaderComponent {
  private readonly hostElement = inject(ElementRef<HTMLElement>);

  mode = input<'default' | 'compact'>('default');
  profileMenuOpen = signal(false);

  toggleProfileMenu(): void {
    this.profileMenuOpen.update(open => !open);
  }

  closeProfileMenu(): void {
    this.profileMenuOpen.set(false);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as Node | null;
    if (target && !this.hostElement.nativeElement.contains(target)) {
      this.closeProfileMenu();
    }
  }
}
