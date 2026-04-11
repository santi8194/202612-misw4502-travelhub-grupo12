import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface UserProfile {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    partner_id: string | null;
    roles: string[];
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    readonly accessTokenMinutes = 15;
    readonly idleTimeoutMinutes = 5;
    readonly refreshTokenDays = 7;

    // Conexión con el backend Auth-Service usando environment
    private apiUrl = environment.apiBaseUrl;
    private sessionExpiryStorageKey = 'session_expiry_at';
    private lastActivityStorageKey = 'session_last_activity_at';
    private inactivityTimeoutId: number | null = null;
    private lastTrackedActivityAt = 0;

    // Subject reactivo para comunicar el estado a cualquier componente (ej. Navbar)
    private authStatusSubject = new BehaviorSubject<boolean>(this.hasToken());
    private sessionExpirySubject = new BehaviorSubject<Date | null>(this.readStoredSessionExpiry());
    public isAuthenticated$ = this.authStatusSubject.asObservable();
    public sessionExpiry$ = this.sessionExpirySubject.asObservable();

    constructor(
        private http: HttpClient,
        private router: Router
    ) {
        this.registerActivityListeners();
        if (this.hasToken()) {
            this.restoreSessionTracking();
        }
    }

    login(credentials: any): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credentials).pipe(
            tap(response => {
                if (response.access_token) {
                    localStorage.setItem('access_token', response.access_token);
                    localStorage.setItem('refresh_token', response.refresh_token);
                    this.markActivity();
                    this.authStatusSubject.next(true); // Emitir autenticación exitosa
                }
            })
        );
    }

    logout(redirectToLogin = false): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem(this.sessionExpiryStorageKey);
        localStorage.removeItem(this.lastActivityStorageKey);
        this.clearInactivityTimeout();
        this.sessionExpirySubject.next(null);
        this.authStatusSubject.next(false); // Emitir des-autenticación

        if (redirectToLogin) {
            void this.router.navigate(['/login']);
        }
    }

    getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    getSessionExpiry(): Date | null {
        return this.sessionExpirySubject.value;
    }

    isAuthenticated(): boolean {
        return this.authStatusSubject.value;
    }

    getCurrentUser(): Observable<UserProfile> {
        return this.http.get<UserProfile>(`${this.apiUrl}/me`);
    }

    private hasToken(): boolean {
        // Es posible agregar lógica de decodificación o chequeo JWT expirado luego
        return !!localStorage.getItem('access_token');
    }

    private registerActivityListeners(): void {
        if (typeof window === 'undefined') {
            return;
        }

        ['click', 'keydown', 'mousemove', 'scroll', 'touchstart'].forEach((eventName) => {
            window.addEventListener(eventName, () => this.handleUserActivity(), { passive: true });
        });
    }

    private handleUserActivity(): void {
        if (!this.authStatusSubject.value) {
            return;
        }

        const now = Date.now();
        if (now - this.lastTrackedActivityAt < 1000) {
            return;
        }

        this.lastTrackedActivityAt = now;
        this.markActivity(now);
    }

    private markActivity(timestamp = Date.now()): void {
        const expiryDate = new Date(timestamp + this.idleTimeoutMinutes * 60 * 1000);
        localStorage.setItem(this.lastActivityStorageKey, new Date(timestamp).toISOString());
        localStorage.setItem(this.sessionExpiryStorageKey, expiryDate.toISOString());
        this.sessionExpirySubject.next(expiryDate);
        this.scheduleInactivityLogout(expiryDate);
    }

    private restoreSessionTracking(): void {
        const storedExpiry = this.readStoredSessionExpiry();
        if (storedExpiry === null) {
            this.markActivity();
            return;
        }

        if (storedExpiry.getTime() <= Date.now()) {
            this.logout(true);
            return;
        }

        this.sessionExpirySubject.next(storedExpiry);
        this.scheduleInactivityLogout(storedExpiry);
    }

    private readStoredSessionExpiry(): Date | null {
        const storedValue = localStorage.getItem(this.sessionExpiryStorageKey);
        if (!storedValue) {
            return null;
        }

        const parsedDate = new Date(storedValue);
        return Number.isNaN(parsedDate.getTime()) ? null : parsedDate;
    }

    private scheduleInactivityLogout(expiryDate: Date): void {
        this.clearInactivityTimeout();

        const millisecondsUntilLogout = expiryDate.getTime() - Date.now();
        if (millisecondsUntilLogout <= 0) {
            this.logout(true);
            return;
        }

        this.inactivityTimeoutId = window.setTimeout(() => {
            this.logout(true);
        }, millisecondsUntilLogout);
    }

    private clearInactivityTimeout(): void {
        if (this.inactivityTimeoutId !== null) {
            clearTimeout(this.inactivityTimeoutId);
            this.inactivityTimeoutId = null;
        }
    }
}
