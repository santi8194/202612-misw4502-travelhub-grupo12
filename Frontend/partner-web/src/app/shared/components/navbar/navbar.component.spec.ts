import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { Router, provideRouter } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { NavbarComponent } from './navbar.component';
import { AuthService } from '../../../core/services/auth.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

describe('NavbarComponent', () => {
  let component: NavbarComponent;
  let fixture: ComponentFixture<NavbarComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: Router;
  let isAuthenticatedSubject: BehaviorSubject<boolean>;

  beforeEach(async () => {
    isAuthenticatedSubject = new BehaviorSubject<boolean>(true);
    authService = jasmine.createSpyObj('AuthService', ['logout'], {
      isAuthenticated$: isAuthenticatedSubject.asObservable(),
    });

    await TestBed.configureTestingModule({
      imports: [NavbarComponent, TranslateModule.forRoot()],
      providers: [
        { provide: AuthService, useValue: authService },
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
    spyOn(router, 'navigate');

    fixture = TestBed.createComponent(NavbarComponent);
    component = fixture.componentInstance;

    const translateService = TestBed.inject(TranslateService);
    translateService.setTranslation('en', {
      NAVBAR: {
        SEARCH_PLACEHOLDER: 'Start your search',
        LANG_LABEL: 'English (EN)',
        LOGOUT: 'Sign out',
        REGISTER: 'Register',
        LOGIN: 'Sign in'
      }
    });
    translateService.use('en');

    fixture.detectChanges();
  });

  // ─── Creation ───

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should start with dropdown closed', () => {
    expect(component.isDropdownOpen).toBeFalse();
  });

  // ─── toggleDropdown ───

  it('should toggle dropdown open and closed', () => {
    const event = new Event('click');
    spyOn(event, 'stopPropagation');

    component.toggleDropdown(event);
    expect(component.isDropdownOpen).toBeTrue();
    expect(event.stopPropagation).toHaveBeenCalled();

    component.toggleDropdown(event);
    expect(component.isDropdownOpen).toBeFalse();
  });

  // ─── closeDropdown (HostListener) ───

  it('should close dropdown on document click', () => {
    component.isDropdownOpen = true;
    component.closeDropdown();
    expect(component.isDropdownOpen).toBeFalse();
  });

  // ─── logout ───

  it('should call authService.logout, close dropdown, and navigate to /login', () => {
    component.isDropdownOpen = true;

    component.logout();

    expect(authService.logout).toHaveBeenCalled();
    expect(component.isDropdownOpen).toBeFalse();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  // ─── Template: authenticated state ───

  it('should show "Cerrar sesión" when authenticated', () => {
    isAuthenticatedSubject.next(true);
    component.isDropdownOpen = true;
    fixture.detectChanges();

    const logoutBtn = fixture.nativeElement.querySelector('[data-testid="btn-logout"]');
    expect(logoutBtn).toBeTruthy();
    expect(logoutBtn.textContent).toContain('Sign out');
  });

  it('should show "Iniciar sesión" when not authenticated', () => {
    isAuthenticatedSubject.next(false);
    component.isDropdownOpen = true;
    fixture.detectChanges();

    const logoutBtn = fixture.nativeElement.querySelector('[data-testid="btn-logout"]');
    expect(logoutBtn).toBeNull();

    const loginLink = fixture.nativeElement.querySelector('.dropdown-menu');
    expect(loginLink.textContent).toContain('Sign in');
  });

  // ─── Template: logo ───

  it('should display the TravelHub logo', () => {
    const logo = fixture.nativeElement.querySelector('.logo');
    expect(logo).toBeTruthy();
    expect(logo.textContent).toContain('TravelHub');
  });

  // ─── toggleLangDropdown ───

  it('should toggle lang dropdown open and close user dropdown', () => {
    const event = new Event('click');
    spyOn(event, 'stopPropagation');

    component.isDropdownOpen = true;
    component.toggleLangDropdown(event);

    expect(component.isLangDropdownOpen).toBeTrue();
    expect(component.isDropdownOpen).toBeFalse();
    expect(event.stopPropagation).toHaveBeenCalled();
  });

  it('should toggle lang dropdown closed on second call', () => {
    const event = new Event('click');
    component.toggleLangDropdown(event);
    expect(component.isLangDropdownOpen).toBeTrue();
    component.toggleLangDropdown(event);
    expect(component.isLangDropdownOpen).toBeFalse();
  });

  // ─── toggleDropdown should close lang dropdown ───

  it('toggleDropdown should close lang dropdown', () => {
    const event = new Event('click');
    component.isLangDropdownOpen = true;
    component.toggleDropdown(event);
    expect(component.isLangDropdownOpen).toBeFalse();
    expect(component.isDropdownOpen).toBeTrue();
  });

  // ─── switchLang ───

  it('should switch language and close lang dropdown', () => {
    const translateService = TestBed.inject(TranslateService);
    spyOn(translateService, 'use').and.callThrough();

    component.isLangDropdownOpen = true;
    component.switchLang('fr');

    expect(translateService.use).toHaveBeenCalledWith('fr');
    expect(component.isLangDropdownOpen).toBeFalse();
  });

  // ─── currentLang ───

  it('should return current language code', () => {
    const translateService = TestBed.inject(TranslateService);
    translateService.use('es');
    expect(component.currentLang).toBe('es');
  });

  // ─── currentLangLabel ───

  it('should return language label for current language', () => {
    const translateService = TestBed.inject(TranslateService);
    translateService.use('en');
    expect(component.currentLangLabel).toBe('English (EN)');
  });

  it('should return fallback label for unknown language', () => {
    const translateService = TestBed.inject(TranslateService);
    translateService.use('xx');
    // Falls back to ?? 'English (EN)' if not found
    expect(component.currentLangLabel).toBeTruthy();
  });

  // ─── closeDropdown also closes lang dropdown ───

  it('closeDropdown should close both dropdowns', () => {
    component.isDropdownOpen = true;
    component.isLangDropdownOpen = true;
    component.closeDropdown();
    expect(component.isDropdownOpen).toBeFalse();
    expect(component.isLangDropdownOpen).toBeFalse();
  });
});
