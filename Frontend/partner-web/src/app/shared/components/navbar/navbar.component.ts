import { Component, HostListener } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AsyncPipe } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';

@Component({
    selector: 'app-navbar',
    imports: [RouterLink, AsyncPipe],
    templateUrl: './navbar.component.html',
    styleUrl: './navbar.component.scss'
})
export class NavbarComponent {
    isDropdownOpen = false;

    constructor(
        public authService: AuthService,
        private router: Router
    ) { }

    toggleDropdown(event: Event) {
        event.stopPropagation();
        this.isDropdownOpen = !this.isDropdownOpen;
    }

    @HostListener('document:click')
    closeDropdown() {
        this.isDropdownOpen = false;
    }

    logout() {
        this.authService.logout();
        this.isDropdownOpen = false;
        this.router.navigate(['/login']);
    }
}
