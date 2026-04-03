import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    // Conexión con el backend Auth-Service expuesto en puertos de Docker
    private apiUrl = 'http://localhost:8003/auth';

    // Subject reactivo para comunicar el estado a cualquier componente (ej. Navbar)
    private authStatusSubject = new BehaviorSubject<boolean>(this.hasToken());
    public isAuthenticated$ = this.authStatusSubject.asObservable();

    constructor(private http: HttpClient) { }

    login(credentials: any): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credentials).pipe(
            tap(response => {
                if (response.access_token) {
                    localStorage.setItem('access_token', response.access_token);
                    this.authStatusSubject.next(true); // Emitir autenticación exitosa
                }
            })
        );
    }

    logout(): void {
        localStorage.removeItem('access_token');
        this.authStatusSubject.next(false); // Emitir des-autenticación
    }

    getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    isAuthenticated(): boolean {
        return this.authStatusSubject.value;
    }

    private hasToken(): boolean {
        // Es posible agregar lógica de decodificación o chequeo JWT expirado luego
        return !!localStorage.getItem('access_token');
    }
}
