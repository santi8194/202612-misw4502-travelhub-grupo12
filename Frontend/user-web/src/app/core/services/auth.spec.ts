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
};

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

      const req = httpTesting.expectOne(`${BASE}/confirm`);
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
    it('should store all token fields and email in localStorage', () => {
      service.saveSession(mockTokens, 'juan@ejemplo.com');

      expect(localStorage.getItem('th_access_token')).toBe('acc-token-xyz');
      expect(localStorage.getItem('th_refresh_token')).toBe('ref-token-xyz');
      expect(localStorage.getItem('th_token_type')).toBe('Bearer');
      expect(localStorage.getItem('th_user_email')).toBe('juan@ejemplo.com');
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
  });
});
