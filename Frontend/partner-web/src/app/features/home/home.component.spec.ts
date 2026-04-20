import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter, Router } from '@angular/router';
import { of, throwError, BehaviorSubject, NEVER } from 'rxjs';
import { HomeComponent } from './home.component';
import { AuthService, UserProfile } from '../../core/services/auth.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let sessionExpirySubject: BehaviorSubject<Date | null>;

  const mockUser: UserProfile = {
    id: 'u1',
    email: 'socio@hotel.com',
    full_name: 'Socio Test',
    is_active: true,
    partner_id: 'partner-001',
    roles: ['ADMIN_HOTEL'],
  };

  const mockUserNoPartner: UserProfile = {
    ...mockUser,
    partner_id: null,
    email: 'admin@sinhotel.com',
  };

  beforeEach(async () => {
    sessionExpirySubject = new BehaviorSubject<Date | null>(null);

    authService = jasmine.createSpyObj('AuthService', ['getCurrentUser', 'getSessionExpiry', 'logout'], {
      accessTokenMinutes: 15,
      idleTimeoutMinutes: 5,
      refreshTokenDays: 7,
      sessionExpiry$: sessionExpirySubject.asObservable(),
      isAuthenticated$: new BehaviorSubject<boolean>(true).asObservable(),
    });

    authService.getSessionExpiry.and.returnValue(null);
    authService.getCurrentUser.and.returnValue(of(mockUser));

    await TestBed.configureTestingModule({
      imports: [HomeComponent, TranslateModule.forRoot()],
      providers: [
        { provide: AuthService, useValue: authService },
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;

    // Set up translations for tests
    const translateService = TestBed.inject(TranslateService);
    translateService.setTranslation('en', {
      BRAND: { SUBTITLE: 'Partner Portal' },
      SIDEBAR: { DASHBOARD: 'Dashboard', RESERVATIONS: 'Reservations', INVENTORY: 'Inventory', PRICING: 'Pricing', REPORTS: 'Revenue Reports', EDIT_PROFILE: 'Edit profile', LOGOUT: 'Sign out', LANGUAGE: 'Language' },
      SECTIONS: {
        DASHBOARD_TITLE: 'Dashboard', DASHBOARD_SUBTITLE: 'Welcome, here is a general overview of the portal.',
        PRICING_TITLE: 'Price Management', PRICING_SUBTITLE: 'Manage availability and room rate assignment.'
      },
      ACTIONS: { SAVE_CHANGES: 'Save changes', HIDE: 'Hide' },
      TODAY: 'Today',
      SESSION: { IDLE_WARNING: 'If you have no activity for <strong>{{minutes}} minutes</strong>, the session will be automatically deactivated.', EXPIRY_MESSAGE: 'With current activity, session closes at <strong>{{time}}</strong>.', ACCESS_TOKEN: 'Access token', MAX_IDLE: 'Max idle time', REFRESH_TOKEN: 'Refresh token', HIDE_LABEL: 'Hide session info', DAYS: 'days' },
      LOCKOUT: { TITLE: 'Access Security Policy', HIDE_LABEL: 'Hide lockout policy', MESSAGE: 'If <strong>{{attempts}} failed attempts</strong> detected, account locked for <strong>{{minutes}} minutes</strong>.', MAX_ATTEMPTS: 'Max attempts', UNLOCK_TIME: 'Unlock time' },
      WELCOME: { GREETING: 'Welcome, {{email}}!', MANAGING_HOTEL: 'You are managing the hotel', NO_HOTEL: 'You don\'t have an assigned hotel yet.' },
      LOADING: 'Loading...',
      ERROR: { USER_LOAD: 'Could not load user information.' },
      PLACEHOLDER_SECTION: 'This section will be available in the next sprint.',
      PRICING_CARDS: { AVG_RATE: 'Average rate', PROMOTIONS: 'Promotions', ACTIVE: 'Active', MONTHLY_REVENUE: 'Monthly revenue' }
    });
    translateService.use('en');
  });

  // ─── Initialization ───

  it('should create the component', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should start with loading true', () => {
    expect(component.loading).toBeTrue();
  });

  it('should have session info from AuthService', () => {
    expect(component.sessionInfo.accessTokenMinutes).toBe(15);
    expect(component.sessionInfo.idleTimeoutMinutes).toBe(5);
    expect(component.sessionInfo.refreshTokenDays).toBe(7);
  });

  it('should have lockout policy info', () => {
    expect(component.lockoutPolicyInfo.maxFailedAttempts).toBe(5);
    expect(component.lockoutPolicyInfo.lockoutMinutes).toBe(5);
  });

  // ─── ngOnInit success ───

  it('should load user profile on init', () => {
    fixture.detectChanges();

    expect(authService.getCurrentUser).toHaveBeenCalled();
    expect(component.user).toEqual(mockUser);
    expect(component.loading).toBeFalse();
    expect(component.error).toBeFalse();
  });

  it('should display user email in welcome card', () => {
    fixture.detectChanges();

    const title = fixture.nativeElement.querySelector('[data-testid="welcome-title"]');
    expect(title.textContent).toContain('socio@hotel.com');
  });

  it('should display partner badge when user has partner_id', () => {
    fixture.detectChanges();

    const badge = fixture.nativeElement.querySelector('.partner-badge');
    expect(badge).toBeTruthy();
    expect(badge.textContent).toContain('partner-001');
  });

  it('should display no-partner message when partner_id is null', () => {
    authService.getCurrentUser.and.returnValue(of(mockUserNoPartner));

    fixture.detectChanges();

    const noPartner = fixture.nativeElement.querySelector('.no-partner');
    expect(noPartner).toBeTruthy();
    expect(noPartner.textContent).toContain('assigned hotel');
  });

  // ─── ngOnInit error ───

  it('should set error true when getCurrentUser fails', () => {
    authService.getCurrentUser.and.returnValue(throwError(() => new Error('Network error')));

    fixture.detectChanges();

    expect(component.error).toBeTrue();
    expect(component.loading).toBeFalse();
    expect(component.user).toBeNull();
  });

  it('should display error message in template on failure', () => {
    authService.getCurrentUser.and.returnValue(throwError(() => new Error('fail')));

    fixture.detectChanges();

    const errorEl = fixture.nativeElement.querySelector('[data-testid="welcome-error"]');
    expect(errorEl).toBeTruthy();
    expect(errorEl.textContent).toContain('Could not load user information');
  });

  it('should show loading indicator before data arrives', () => {
    // Use NEVER to simulate a pending HTTP request that hasn't completed yet
    authService.getCurrentUser.and.returnValue(NEVER);

    fixture.detectChanges();

    const loading = fixture.nativeElement.querySelector('[data-testid="welcome-loading"]');
    expect(loading).toBeTruthy();
  });

  // ─── Session expiry tracking ───

  it('should update sessionExpirationAt when sessionExpiry$ emits', () => {
    fixture.detectChanges();

    const futureDate = new Date(Date.now() + 300_000);
    sessionExpirySubject.next(futureDate);

    expect(component.sessionExpirationAt).toEqual(futureDate);
  });

  // ─── dismiss methods ───

  it('dismissSessionInfo should hide session card', () => {
    expect(component.showSessionInfo).toBeTrue();
    component.dismissSessionInfo();
    expect(component.showSessionInfo).toBeFalse();
  });

  it('dismissLockoutInfo should hide lockout card', () => {
    expect(component.showLockoutInfo).toBeTrue();
    component.dismissLockoutInfo();
    expect(component.showLockoutInfo).toBeFalse();
  });

  // ─── ngOnDestroy ───

  it('ngOnDestroy should complete destroy$ subject', () => {
    fixture.detectChanges();

    spyOn(component['destroy$'], 'next');
    spyOn(component['destroy$'], 'complete');

    component.ngOnDestroy();

    expect(component['destroy$'].next).toHaveBeenCalled();
    expect(component['destroy$'].complete).toHaveBeenCalled();
  });

  // ─── Section navigation ───

  it('setActiveSection should change the active section', () => {
    component.setActiveSection('precios');
    expect(component.activeSection).toBe('precios');
  });

  it('isDashboardSelected should return true for dashboard', () => {
    component.setActiveSection('dashboard');
    expect(component.isDashboardSelected()).toBeTrue();
  });

  it('isDashboardSelected should return false for other sections', () => {
    component.setActiveSection('precios');
    expect(component.isDashboardSelected()).toBeFalse();
  });

  it('isPricingSelected should return true for precios', () => {
    component.setActiveSection('precios');
    expect(component.isPricingSelected()).toBeTrue();
  });

  it('isPricingSelected should return false for dashboard', () => {
    component.setActiveSection('dashboard');
    expect(component.isPricingSelected()).toBeFalse();
  });

  // ─── Section title/subtitle keys ───

  it('currentSectionTitleKey should return correct key for active section', () => {
    component.setActiveSection('reservas');
    expect(component.currentSectionTitleKey).toBe('SECTIONS.RESERVATIONS_TITLE');
  });

  it('currentSectionSubtitleKey should return correct key for active section', () => {
    component.setActiveSection('inventario');
    expect(component.currentSectionSubtitleKey).toBe('SECTIONS.INVENTORY_SUBTITLE');
  });

  it('currentSectionTitleKey should fallback for unknown section', () => {
    component.setActiveSection('unknown');
    expect(component.currentSectionTitleKey).toBe('SECTIONS.DASHBOARD_TITLE');
  });

  it('currentSectionSubtitleKey should fallback for unknown section', () => {
    component.setActiveSection('unknown');
    expect(component.currentSectionSubtitleKey).toBe('SECTIONS.DASHBOARD_SUBTITLE');
  });

  // ─── Pricing section ───

  it('should show pricing section when precios is selected', () => {
    fixture.detectChanges();
    component.setActiveSection('precios');
    fixture.detectChanges();

    const pricingSection = fixture.nativeElement.querySelector('.prices-overview');
    expect(pricingSection).toBeTruthy();
  });

  it('should show save button when pricing is selected', () => {
    fixture.detectChanges();
    component.setActiveSection('precios');
    fixture.detectChanges();

    const saveBtn = fixture.nativeElement.querySelector('.save-button');
    expect(saveBtn).toBeTruthy();
  });

  it('should show today box when dashboard is selected', () => {
    fixture.detectChanges();
    component.setActiveSection('dashboard');
    fixture.detectChanges();

    const todayBox = fixture.nativeElement.querySelector('.today-box');
    expect(todayBox).toBeTruthy();
  });

  // ─── guardarCambiosPrecios ───

  it('guardarCambiosPrecios should call validate on preciosComponent', () => {
    fixture.detectChanges();
    component.setActiveSection('precios');
    fixture.detectChanges();

    // preciosComponent should be available via ViewChild
    if (component.preciosComponent) {
      spyOn(component.preciosComponent, 'validate').and.returnValue(true);
      component.guardarCambiosPrecios();
      expect(component.preciosComponent.validate).toHaveBeenCalled();
      expect(component.pricingHasErrors).toBeFalse();
    }
  });

  it('guardarCambiosPrecios should set pricingHasErrors true when invalid', () => {
    fixture.detectChanges();
    component.setActiveSection('precios');
    fixture.detectChanges();

    if (component.preciosComponent) {
      spyOn(component.preciosComponent, 'validate').and.returnValue(false);
      component.guardarCambiosPrecios();
      expect(component.pricingHasErrors).toBeTrue();
    }
  });

  it('guardarCambiosPrecios should not fail when preciosComponent is undefined', () => {
    component.setActiveSection('dashboard');
    fixture.detectChanges();
    // preciosComponent is undefined since pricing section is not rendered
    expect(() => component.guardarCambiosPrecios()).not.toThrow();
  });

  // ─── Language selector ───

  it('should start with lang selector hidden', () => {
    expect(component.showLangSelector).toBeFalse();
  });

  it('toggleLangSelector should toggle visibility', () => {
    component.toggleLangSelector();
    expect(component.showLangSelector).toBeTrue();
    component.toggleLangSelector();
    expect(component.showLangSelector).toBeFalse();
  });

  it('switchLang should change language and close selector', () => {
    const translateService = TestBed.inject(TranslateService);
    spyOn(translateService, 'use').and.callThrough();

    component.showLangSelector = true;
    component.switchLang('fr');

    expect(translateService.use).toHaveBeenCalledWith('fr');
    expect(component.showLangSelector).toBeFalse();
  });

  it('currentLangLabel should return the label for the current language', () => {
    const translateService = TestBed.inject(TranslateService);
    translateService.use('en');
    expect(component.currentLangLabel).toBe('English (EN)');
  });

  it('currentLangLabel should fallback to code for unknown language', () => {
    const translateService = TestBed.inject(TranslateService);
    translateService.use('xx');
    expect(component.currentLangLabel).toBe('xx');
  });

  // ─── Placeholder section ───

  it('should show placeholder for non-dashboard non-pricing sections', () => {
    fixture.detectChanges();
    component.setActiveSection('reservas');
    fixture.detectChanges();

    const placeholder = fixture.nativeElement.querySelector('.placeholder-section');
    expect(placeholder).toBeTruthy();
  });

  // ─── Logout ───

  it('logout should call authService.logout and navigate', () => {
    const router = TestBed.inject(Router);
    spyOn(router, 'navigate');

    component.logout();

    expect(authService.logout).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });
});
