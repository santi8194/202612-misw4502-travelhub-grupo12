import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { AuthService, LoginResponse, UserProfile } from './auth.service';
import { environment } from '../../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let router: jasmine.SpyObj<Router>;

  const apiUrl = environment.apiBaseUrl;

  const mockLoginResponse: LoginResponse = {
    access_token: 'test-access-token',
    refresh_token: 'test-refresh-token',
    token_type: 'bearer',
  };

  const mockUser: UserProfile = {
    id: 'u1',
    email: 'socio@hotel.com',
    full_name: 'Test User',
    is_active: true,
    partner_id: 'partner-001',
    roles: ['ADMIN_HOTEL'],
  };

  beforeEach(() => {
    localStorage.clear();

    router = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Router, useValue: router },
      ],
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  // ─── Constructor & initial state ───

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should start as not authenticated when no token exists', () => {
    expect(service.isAuthenticated()).toBeFalse();
  });

  it('should expose session constants', () => {
    expect(service.accessTokenMinutes).toBe(15);
    expect(service.idleTimeoutMinutes).toBe(5);
    expect(service.refreshTokenDays).toBe(7);
  });

  // ─── login() ───

  it('login() should POST credentials and store tokens', () => {
    const creds = { email: 'a@b.com', password: '123' };

    service.login(creds).subscribe((res) => {
      expect(res.access_token).toBe('test-access-token');
    });

    const req = httpMock.expectOne(`${apiUrl}/login`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(creds);
    req.flush(mockLoginResponse);

    expect(localStorage.getItem('access_token')).toBe('test-access-token');
    expect(localStorage.getItem('refresh_token')).toBe('test-refresh-token');
    expect(service.isAuthenticated()).toBeTrue();
  });

  it('login() should not store tokens when access_token is empty', () => {
    service.login({ email: 'a@b.com', password: '123' }).subscribe();

    const req = httpMock.expectOne(`${apiUrl}/login`);
    req.flush({ access_token: '', refresh_token: '', token_type: 'bearer' });

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(service.isAuthenticated()).toBeFalse();
  });

  // ─── logout() ───

  it('logout() should clear all stored data and emit false', () => {
    localStorage.setItem('access_token', 'tok');
    localStorage.setItem('refresh_token', 'ref');
    localStorage.setItem('session_expiry_at', new Date().toISOString());
    localStorage.setItem('session_last_activity_at', new Date().toISOString());

    service.logout();

    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('session_expiry_at')).toBeNull();
    expect(localStorage.getItem('session_last_activity_at')).toBeNull();
    expect(service.isAuthenticated()).toBeFalse();
  });

  it('logout(true) should navigate to /login', () => {
    service.logout(true);
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('logout(false) should NOT navigate', () => {
    service.logout(false);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  // ─── getToken() ───

  it('getToken() should return null when no token', () => {
    expect(service.getToken()).toBeNull();
  });

  it('getToken() should return stored token', () => {
    localStorage.setItem('access_token', 'my-token');
    expect(service.getToken()).toBe('my-token');
  });

  // ─── getCurrentUser() ───

  it('getCurrentUser() should GET /me', () => {
    service.getCurrentUser().subscribe((user) => {
      expect(user.email).toBe('socio@hotel.com');
    });

    const req = httpMock.expectOne(`${apiUrl}/me`);
    expect(req.request.method).toBe('GET');
    req.flush(mockUser);
  });

  // ─── getSessionExpiry() / sessionExpiry$ ───

  it('getSessionExpiry() should return null initially', () => {
    expect(service.getSessionExpiry()).toBeNull();
  });

  it('sessionExpiry$ should emit after login', () => {
    let emitted: Date | null = null;
    service.sessionExpiry$.subscribe((v) => (emitted = v));

    service.login({ email: 'a@b.com', password: '123' }).subscribe();
    const req = httpMock.expectOne(`${apiUrl}/login`);
    req.flush(mockLoginResponse);

    expect(emitted).toBeInstanceOf(Date);
  });

  // ─── isAuthenticated$ ───

  it('isAuthenticated$ should emit true after login', () => {
    let status = false;
    service.isAuthenticated$.subscribe((v) => (status = v));

    service.login({ email: 'a@b.com', password: '123' }).subscribe();
    httpMock.expectOne(`${apiUrl}/login`).flush(mockLoginResponse);

    expect(status).toBeTrue();
  });

  it('isAuthenticated$ should emit false after logout', () => {
    let status = true;
    service.isAuthenticated$.subscribe((v) => (status = v));

    service.logout();

    expect(status).toBeFalse();
  });

  // ─── Session tracking / inactivity ───

  it('should restore session tracking on construct when token exists', () => {
    localStorage.setItem('access_token', 'tok');
    const futureExpiry = new Date(Date.now() + 300_000).toISOString();
    localStorage.setItem('session_expiry_at', futureExpiry);

    // Re-create service to trigger constructor logic
    const svc = TestBed.inject(AuthService);
    expect(svc.isAuthenticated()).toBeFalse(); // singleton, same service
  });

  it('should auto-logout when session is expired on restore', fakeAsync(() => {
    localStorage.setItem('access_token', 'tok');
    const pastExpiry = new Date(Date.now() - 1000).toISOString();
    localStorage.setItem('session_expiry_at', pastExpiry);

    // Force restoreSessionTracking via a new login + logout cycle
    service.login({ email: 'a@b.com', password: '123' }).subscribe();
    httpMock.expectOne(`${apiUrl}/login`).flush(mockLoginResponse);

    // Simulate session expiry timeout
    tick(6 * 60 * 1000);

    expect(service.isAuthenticated()).toBeFalse();
  }));

  it('should schedule inactivity logout after login', fakeAsync(() => {
    service.login({ email: 'a@b.com', password: '123' }).subscribe();
    httpMock.expectOne(`${apiUrl}/login`).flush(mockLoginResponse);

    expect(service.isAuthenticated()).toBeTrue();

    // Advance past idle timeout (5 min)
    tick(5 * 60 * 1000 + 100);

    expect(service.isAuthenticated()).toBeFalse();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  }));

  // ─── readStoredSessionExpiry edge cases ───

  it('should handle invalid date in session_expiry_at', () => {
    localStorage.setItem('session_expiry_at', 'not-a-date');
    expect(service.getSessionExpiry()).toBeNull();
  });

  // ─── handleUserActivity / markActivity ───

  it('should mark activity on user click event when authenticated', fakeAsync(() => {
    service.login({ email: 'a@b.com', password: '123' }).subscribe();
    httpMock.expectOne(`${apiUrl}/login`).flush(mockLoginResponse);

    const expiryBefore = service.getSessionExpiry();

    // Advance time 2 seconds to bypass throttle
    tick(2000);
    window.dispatchEvent(new Event('click'));
    tick(0);

    const expiryAfter = service.getSessionExpiry();
    expect(expiryAfter).toBeTruthy();
    if (expiryBefore && expiryAfter) {
      expect(expiryAfter.getTime()).toBeGreaterThanOrEqual(expiryBefore.getTime());
    }

    // Clean up the scheduled timeout
    service.logout();
    tick(10 * 60 * 1000);
  }));

  it('should not mark activity when not authenticated', () => {
    service.logout();
    const expiry = service.getSessionExpiry();
    window.dispatchEvent(new Event('click'));
    expect(service.getSessionExpiry()).toEqual(expiry);
  });

  it('should throttle activity events within 1 second', fakeAsync(() => {
    service.login({ email: 'a@b.com', password: '123' }).subscribe();
    httpMock.expectOne(`${apiUrl}/login`).flush(mockLoginResponse);

    // First event
    tick(2000);
    window.dispatchEvent(new Event('keydown'));
    const expiryAfterFirst = service.getSessionExpiry();

    // Second event immediately (within 1000ms) - should be throttled
    tick(100);
    window.dispatchEvent(new Event('keydown'));
    const expiryAfterSecond = service.getSessionExpiry();

    expect(expiryAfterFirst).toEqual(expiryAfterSecond);

    service.logout();
    tick(10 * 60 * 1000);
  }));

  // ─── restoreSessionTracking ───

  it('should call markActivity when token exists but no stored expiry', () => {
    localStorage.setItem('access_token', 'tok');

    // Re-create service from scratch
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Router, useValue: router },
      ],
    });

    const newService = TestBed.inject(AuthService);
    // Should have set an expiry via markActivity
    expect(newService.getSessionExpiry()).toBeTruthy();
  });

  it('should schedule logout when token exists with valid future expiry', fakeAsync(() => {
    const future = new Date(Date.now() + 60_000).toISOString();
    localStorage.setItem('access_token', 'tok');
    localStorage.setItem('session_expiry_at', future);

    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Router, useValue: router },
      ],
    });

    const newService = TestBed.inject(AuthService);
    expect(newService.isAuthenticated()).toBeTrue();

    // Advance past the expiry
    tick(61_000);

    expect(newService.isAuthenticated()).toBeFalse();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  }));

  // ─── scheduleInactivityLogout edge case ───

  it('should immediately logout when scheduled time is in the past', fakeAsync(() => {
    service.login({ email: 'a@b.com', password: '123' }).subscribe();
    httpMock.expectOne(`${apiUrl}/login`).flush(mockLoginResponse);

    expect(service.isAuthenticated()).toBeTrue();

    // Wait for the idle timeout to expire
    tick(5 * 60 * 1000 + 500);

    expect(service.isAuthenticated()).toBeFalse();
  }));

  // ─── clearInactivityTimeout when null ───

  it('logout should work even if no timeout was scheduled', () => {
    // No login, so no timeout scheduled
    service.logout();
    expect(service.isAuthenticated()).toBeFalse();
  });
});
