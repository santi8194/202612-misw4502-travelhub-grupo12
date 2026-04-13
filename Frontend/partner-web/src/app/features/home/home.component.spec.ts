import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of, throwError, BehaviorSubject, NEVER } from 'rxjs';
import { HomeComponent } from './home.component';
import { AuthService, UserProfile } from '../../core/services/auth.service';

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

    authService = jasmine.createSpyObj('AuthService', ['getCurrentUser', 'getSessionExpiry'], {
      accessTokenMinutes: 15,
      idleTimeoutMinutes: 5,
      refreshTokenDays: 7,
      sessionExpiry$: sessionExpirySubject.asObservable(),
      isAuthenticated$: new BehaviorSubject<boolean>(true).asObservable(),
    });

    authService.getSessionExpiry.and.returnValue(null);
    authService.getCurrentUser.and.returnValue(of(mockUser));

    await TestBed.configureTestingModule({
      imports: [HomeComponent],
      providers: [
        { provide: AuthService, useValue: authService },
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
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
    expect(noPartner.textContent).toContain('No tienes un hotel asignado');
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
    expect(errorEl.textContent).toContain('No se pudo cargar la información del usuario');
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
});
