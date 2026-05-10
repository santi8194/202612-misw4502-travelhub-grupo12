import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { AuthService } from './auth';
import { AuthTokenResponse } from '../../models/auth.interface';
import { environment } from '../../../environments/environment';

const BASE = environment.authApiUrl;

const mockTokens: AuthTokenResponse = {
  access_token: 'acc-token-xyz',
  refresh_token: 'ref-token-xyz',
  token_type: 'Bearer',
  user_id: 'test-user-uuid-001',
};

function buildJwt(payload: Record<string, unknown>): string {
  const encoded = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
  return `header.${encoded}.signature`;
}

describe('AuthService', () => {
  let service: AuthService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(AuthService);
    httpTesting = TestBed.inject(HttpTestingController);
    localStorage.clear();
  });

  afterEach(() => {
    httpTesting.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  // ─── register ───────────────────────────────────
  describe('register()', () => {
    it('should POST to /register with the provided payload', () => {
      const payload = {
        email: 'juan@ejemplo.com',
        password: 'Clave1234!',
        first_name: 'Juan',
        last_name: 'Pérez',
        phone_number: '+573001112233',
      };

      service.register(payload).subscribe();

      const req = httpTesting.expectOne(`${BASE}/register`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(payload);
      req.flush({ message: 'User created' });
    });
  });

  // ─── confirmRegistration ────────────────────────
  describe('confirmRegistration()', () => {
    it('should POST to /confirm with email and code', () => {
      const payload = { email: 'juan@ejemplo.com', code: '123456' };

      service.confirmRegistration(payload).subscribe();

      const req = httpTesting.expectOne(`${BASE}/register/confirm`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(payload);
      req.flush({ message: 'Confirmed' });
    });
  });

  // ─── login ──────────────────────────────────────
  describe('login()', () => {
    it('should POST to /login and return AuthTokenResponse', () => {
      const payload = { email: 'juan@ejemplo.com', password: 'Clave1234!' };
      let result: AuthTokenResponse | undefined;

      service.login(payload).subscribe(r => (result = r));

      const req = httpTesting.expectOne(`${BASE}/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(payload);
      req.flush(mockTokens);

      expect(result).toEqual(mockTokens);
    });
  });

  // ─── saveSession ────────────────────────────────
  describe('saveSession()', () => {
    it('should store tokens, email and user profile fields in localStorage', () => {
      service.saveSession(mockTokens, 'juan@ejemplo.com');

      expect(localStorage.getItem('th_access_token')).toBe('acc-token-xyz');
      expect(localStorage.getItem('th_refresh_token')).toBe('ref-token-xyz');
      expect(localStorage.getItem('th_token_type')).toBe('Bearer');
      expect(localStorage.getItem('th_user_email')).toBe('juan@ejemplo.com');
      expect(localStorage.getItem('th_user_id')).toBe('test-user-uuid-001');
      expect(localStorage.getItem('th_user_name')).toBe('juan');
    });

    it('should resolve user data and expiration from jwt claims', () => {
      const accessToken = buildJwt({
        sub: 'claim-user-001',
        name: 'Ana Maria',
        exp: Math.floor(Date.now() / 1000) + 3600,
      });

      service.saveSession({
        access_token: accessToken,
        refresh_token: 'refresh',
        token_type: 'Bearer',
      }, 'ana@example.com');

      expect(localStorage.getItem('th_user_id')).toBe('claim-user-001');
      expect(localStorage.getItem('th_user_name')).toBe('Ana Maria');
      expect(localStorage.getItem('th_access_token_expires_at')).not.toBeNull();
      expect(service.getCurrentSession()?.expiresAt).toBeGreaterThan(Date.now());
    });

    it('should resolve name from first name claim before falling back to email', () => {
      const accessToken = buildJwt({
        user_id: 'claim-user-002',
        first_name: 'Ana',
        last_name: 'Perez',
        exp: String(Math.floor(Date.now() / 1000) + 3600),
      });

      service.saveSession({
        access_token: accessToken,
        refresh_token: 'refresh',
        token_type: 'Bearer',
      }, 'ana@example.com');

      expect(localStorage.getItem('th_user_name')).toBe('Ana');
    });

    it('should resolve first name from token when last name is missing', () => {
      service.saveSession({
        access_token: 'invalid-token',
        refresh_token: 'refresh',
        token_type: 'Bearer',
        id_usuario: 'token-user-001',
        first_name: 'Ana',
      }, 'ana@example.com');

      expect(localStorage.getItem('th_user_id')).toBe('token-user-001');
      expect(localStorage.getItem('th_user_name')).toBe('Ana');
    });

    it('should fallback to existing user id and default user name when needed', () => {
      localStorage.setItem('user_id', 'legacy-user-001');

      service.saveSession({
        access_token: 'invalid-token',
        refresh_token: 'refresh',
        token_type: 'Bearer',
      }, '');

      expect(localStorage.getItem('th_user_id')).toBe('legacy-user-001');
      expect(localStorage.getItem('th_user_name')).toBe('Usuario');
    });
  });

  // ─── clearSession ───────────────────────────────
  describe('clearSession()', () => {
    it('should remove all session keys from localStorage', () => {
      service.saveSession(mockTokens, 'juan@ejemplo.com');
      service.clearSession();

      expect(localStorage.getItem('th_access_token')).toBeNull();
      expect(localStorage.getItem('th_refresh_token')).toBeNull();
      expect(localStorage.getItem('th_token_type')).toBeNull();
      expect(localStorage.getItem('th_user_email')).toBeNull();
      expect(localStorage.getItem('th_user_id')).toBeNull();
      expect(localStorage.getItem('th_user_name')).toBeNull();
    });
  });

  describe('getCurrentUserId()', () => {
    it('should return user id from active session', () => {
      service.saveSession(mockTokens, 'juan@ejemplo.com');
      expect(service.getCurrentUserId()).toBe('test-user-uuid-001');
    });

    it('should return null when no active session exists', () => {
      expect(service.getCurrentUserId()).toBeNull();
    });
  });

  // ─── isLoggedIn ─────────────────────────────────
  describe('isLoggedIn()', () => {
    it('should return false when no access token is stored', () => {
      expect(service.isLoggedIn()).toBeFalse();
    });

    it('should return true when an access token is present', () => {
      service.saveSession(mockTokens, 'juan@ejemplo.com');
      expect(service.isLoggedIn()).toBeTrue();
    });

    it('should return false after clearSession()', () => {
      service.saveSession(mockTokens, 'juan@ejemplo.com');
      service.clearSession();
      expect(service.isLoggedIn()).toBeFalse();
    });

    it('should rebuild session from stored values when session state is empty', () => {
      const accessToken = buildJwt({
        sub: 'stored-user-001',
        given_name: 'Carlos',
        exp: Math.floor(Date.now() / 1000) + 3600,
      });
      localStorage.setItem('th_access_token', accessToken);
      localStorage.setItem('th_refresh_token', 'refresh');
      localStorage.setItem('th_token_type', 'Bearer');
      localStorage.setItem('th_user_email', 'carlos@example.com');

      expect(service.isLoggedIn()).toBeTrue();
      expect(service.getCurrentUserId()).toBe('stored-user-001');
      expect(localStorage.getItem('th_user_name')).toBe('Carlos');
    });

    it('should use stored expiration timestamp when available', () => {
      localStorage.setItem('th_access_token', 'invalid-token');
      localStorage.setItem('th_refresh_token', 'refresh');
      localStorage.setItem('th_token_type', 'Bearer');
      localStorage.setItem('th_user_email', 'ana@example.com');
      localStorage.setItem('th_user_id', 'stored-user-002');
      localStorage.setItem('th_user_name', 'Ana');
      localStorage.setItem('th_access_token_expires_at', String(Date.now() + 3600000));

      expect(service.isLoggedIn()).toBeTrue();
      expect(service.getCurrentSession()?.expiresAt).toBeGreaterThan(Date.now());
    });

    it('should clear expired stored sessions', () => {
      localStorage.setItem('th_access_token', buildJwt({ sub: 'expired-user' }));
      localStorage.setItem('th_refresh_token', 'refresh');
      localStorage.setItem('th_token_type', 'Bearer');
      localStorage.setItem('th_user_email', 'old@example.com');
      localStorage.setItem('th_access_token_expires_at', String(Date.now() - 1000));

      expect(service.isLoggedIn()).toBeFalse();
      expect(localStorage.getItem('th_access_token')).toBeNull();
    });
  });
});
