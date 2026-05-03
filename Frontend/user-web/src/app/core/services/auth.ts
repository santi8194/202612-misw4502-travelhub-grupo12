import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  AuthTokenResponse,
  ConfirmRegistrationRequest,
  LoginRequest,
  RegisterRequest,
} from '../../models/auth.interface';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly authBaseUrl = environment.authApiUrl;

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
    localStorage.setItem('th_access_token', tokens.access_token);
    localStorage.setItem('th_refresh_token', tokens.refresh_token);
    localStorage.setItem('th_token_type', tokens.token_type);
    localStorage.setItem('th_user_email', email);
  }

  clearSession(): void {
    localStorage.removeItem('th_access_token');
    localStorage.removeItem('th_refresh_token');
    localStorage.removeItem('th_token_type');
    localStorage.removeItem('th_user_email');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('th_access_token');
  }
}
