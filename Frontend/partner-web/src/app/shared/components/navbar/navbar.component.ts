import { Component, HostListener } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AsyncPipe } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
    selector: 'app-navbar',
    standalone: true,
    imports: [RouterLink, AsyncPipe, TranslateModule],
    templateUrl: './navbar.component.html',
    styleUrl: './navbar.component.scss'
})
export class NavbarComponent {
    isDropdownOpen = false;
    isLangDropdownOpen = false;
    readonly availableLanguages = [
        { code: 'en', label: 'English (EN)' },
        { code: 'es', label: 'Español (ES)' },
        { code: 'fr', label: 'Français (FR)' },
        { code: 'pt', label: 'Português (PT)' }
    ];

    constructor(
        public authService: AuthService,
        private router: Router,
        public translate: TranslateService
    ) { }

    get currentLang(): string {
        return this.translate.currentLang || this.translate.defaultLang || 'en';
    }

    get currentLangLabel(): string {
        return this.availableLanguages.find(l => l.code === this.currentLang)?.label ?? 'English (EN)';
    }

    toggleDropdown(event: Event) {
        event.stopPropagation();
        this.isDropdownOpen = !this.isDropdownOpen;
        this.isLangDropdownOpen = false;
    }

    toggleLangDropdown(event: Event) {
        event.stopPropagation();
        this.isLangDropdownOpen = !this.isLangDropdownOpen;
        this.isDropdownOpen = false;
    }

    switchLang(langCode: string) {
        this.translate.use(langCode);
        this.isLangDropdownOpen = false;
    }

    @HostListener('document:click')
    closeDropdown() {
        this.isDropdownOpen = false;
        this.isLangDropdownOpen = false;
    }

    logout() {
        this.authService.logout();
        this.isDropdownOpen = false;
        this.router.navigate(['/login']);
    }
}
