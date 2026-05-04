import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  AuthTokenResponse,
  ConfirmRegistrationRequest,
  LoginRequest,
  RegisterRequest,
} from '../../models/auth.interface';
import { environment } from '../../../environments/environment';

interface AuthSession {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  email: string;
  userId: string;
  userName: string;
  expiresAt: number | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly authBaseUrl = environment.authApiUrl;
  private readonly SESSION_KEYS = {
    accessToken: 'th_access_token',
    refreshToken: 'th_refresh_token',
    tokenType: 'th_token_type',
    userEmail: 'th_user_email',
    userId: 'th_user_id',
    userName: 'th_user_name',
    expiresAt: 'th_access_token_expires_at',
  } as const;

  private readonly sessionState = signal<AuthSession | null>(null);
  readonly session = computed(() => this.sessionState());

  constructor() {
    this.refreshSessionState();
  }

  register(payload: RegisterRequest): Observable<unknown> {
    return this.http.post(`${this.authBaseUrl}/register`, payload);
  }

  confirmRegistration(payload: ConfirmRegistrationRequest): Observable<unknown> {
    return this.http.post(`${this.authBaseUrl}/register/confirm`, payload);
  }

  login(payload: LoginRequest): Observable<AuthTokenResponse> {
    return this.http.post<AuthTokenResponse>(`${this.authBaseUrl}/login`, payload);
  }

  saveSession(tokens: AuthTokenResponse, email: string): void {
    const claims = this.decodeJwtClaims(tokens.access_token);
    const userId = this.resolveUserId(tokens, claims);
    const userName = this.resolveUserName(tokens, claims, email);
    const expiresAt = this.resolveExpiresAt(claims);

    localStorage.setItem(this.SESSION_KEYS.accessToken, tokens.access_token);
    localStorage.setItem(this.SESSION_KEYS.refreshToken, tokens.refresh_token);
    localStorage.setItem(this.SESSION_KEYS.tokenType, tokens.token_type);
    localStorage.setItem(this.SESSION_KEYS.userEmail, email);
    localStorage.setItem(this.SESSION_KEYS.userId, userId);
    localStorage.setItem(this.SESSION_KEYS.userName, userName);

    if (expiresAt) {
      localStorage.setItem(this.SESSION_KEYS.expiresAt, String(expiresAt));
    } else {
      localStorage.removeItem(this.SESSION_KEYS.expiresAt);
    }

    this.sessionState.set({
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      tokenType: tokens.token_type,
      email,
      userId,
      userName,
      expiresAt,
    });
  }

  clearSession(): void {
    localStorage.removeItem(this.SESSION_KEYS.accessToken);
    localStorage.removeItem(this.SESSION_KEYS.refreshToken);
    localStorage.removeItem(this.SESSION_KEYS.tokenType);
    localStorage.removeItem(this.SESSION_KEYS.userEmail);
    localStorage.removeItem(this.SESSION_KEYS.userId);
    localStorage.removeItem(this.SESSION_KEYS.userName);
    localStorage.removeItem(this.SESSION_KEYS.expiresAt);
    localStorage.removeItem('user_id');
    this.sessionState.set(null);
  }

  isLoggedIn(): boolean {
    this.refreshSessionState();
    return !!this.sessionState();
  }

  getCurrentSession(): AuthSession | null {
    this.refreshSessionState();
    return this.sessionState();
  }

  getCurrentUserId(): string | null {
    return this.getCurrentSession()?.userId ?? null;
  }

  private refreshSessionState(): void {
    const accessToken = localStorage.getItem(this.SESSION_KEYS.accessToken);
    const refreshToken = localStorage.getItem(this.SESSION_KEYS.refreshToken);
    const tokenType = localStorage.getItem(this.SESSION_KEYS.tokenType);
    const email = localStorage.getItem(this.SESSION_KEYS.userEmail);

    if (!accessToken || !refreshToken || !tokenType || !email) {
      this.sessionState.set(null);
      return;
    }

    const claims = this.decodeJwtClaims(accessToken);
    const expiresAt = this.resolveStoredExpiresAt(claims);

    if (expiresAt && Date.now() >= expiresAt) {
      this.clearSession();
      return;
    }

    const userId = localStorage.getItem(this.SESSION_KEYS.userId)
      ?? this.resolveUserId({ access_token: accessToken, refresh_token: refreshToken, token_type: tokenType }, claims);
    const userName = localStorage.getItem(this.SESSION_KEYS.userName)
      ?? this.resolveUserName({}, claims, email);

    localStorage.setItem(this.SESSION_KEYS.userId, userId);
    localStorage.setItem(this.SESSION_KEYS.userName, userName);

    if (expiresAt) {
      localStorage.setItem(this.SESSION_KEYS.expiresAt, String(expiresAt));
    }

    this.sessionState.set({
      accessToken,
      refreshToken,
      tokenType,
      email,
      userId,
      userName,
      expiresAt,
    });
  }

  private resolveUserId(tokens: Partial<AuthTokenResponse>, claims: Record<string, unknown>): string {
    const fromToken = this.getFirstString([
      tokens.id_usuario,
      tokens.user_id,
    ]);

    const fromClaims = this.getFirstString([
      claims['id_usuario'],
      claims['user_id'],
      claims['custom:id_usuario'],
      claims['sub'],
    ]);

    const existing = this.getFirstString([
      localStorage.getItem(this.SESSION_KEYS.userId),
      localStorage.getItem('user_id'),
    ]);

    return fromToken ?? fromClaims ?? existing ?? crypto.randomUUID();
  }

  private resolveUserName(
    tokens: Partial<AuthTokenResponse>,
    claims: Record<string, unknown>,
    email: string
  ): string {
    const explicit = this.getFirstString([
      tokens.name,
      claims['name'],
      claims['nombre'],
      claims['given_name'],
      claims['first_name'],
    ]);

    if (explicit) {
      return explicit;
    }

    const firstName = this.getFirstString([tokens.first_name, claims['first_name']]);
    const lastName = this.getFirstString([tokens.last_name, claims['last_name']]);

    if (firstName && lastName) {
      return `${firstName} ${lastName}`;
    }

    if (firstName) {
      return firstName;
    }

    const usernameFromEmail = email.split('@')[0]?.trim();
    if (usernameFromEmail) {
      return usernameFromEmail;
    }

    return 'Usuario';
  }

  private resolveExpiresAt(claims: Record<string, unknown>): number | null {
    const exp = claims['exp'];
    if (typeof exp === 'number' && Number.isFinite(exp)) {
      return exp * 1000;
    }

    if (typeof exp === 'string') {
      const parsed = Number(exp);
      if (Number.isFinite(parsed)) {
        return parsed * 1000;
      }
    }

    return null;
  }

  private resolveStoredExpiresAt(claims: Record<string, unknown>): number | null {
    const stored = localStorage.getItem(this.SESSION_KEYS.expiresAt);
    if (stored) {
      const parsed = Number(stored);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }

    return this.resolveExpiresAt(claims);
  }

  private decodeJwtClaims(token: string): Record<string, unknown> {
    if (!token || token.split('.').length < 2) {
      return {};
    }

    try {
      const payload = token.split('.')[1] ?? '';
      const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
      const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
      const binary = atob(padded);
      const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
      const json = new TextDecoder().decode(bytes);
      const parsed = JSON.parse(json);

      if (parsed && typeof parsed === 'object') {
        return parsed as Record<string, unknown>;
      }

      return {};
    } catch {
      return {};
    }
  }

  private getFirstString(values: unknown[]): string | null {
    for (const value of values) {
      if (typeof value === 'string' && value.trim().length > 0) {
        return value.trim();
      }
    }

    return null;
  }
}
