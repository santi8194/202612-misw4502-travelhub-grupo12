import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const authService = inject(AuthService);
    const router = inject(Router);
    const token = authService.getToken();

    // Clonar el request e inyectar el header Bearer automático si el token existe
    if (token) {
        const clonedReq = req.clone({
            headers: req.headers.set('Authorization', `Bearer ${token}`)
        });
        return next(clonedReq).pipe(
            catchError((error) => {
                if (error.status === 401) {
                    authService.logout();
                    void router.navigate(['/login']);
                }
                return throwError(() => error);
            })
        );
    }

    // Dejar que la petición pase directo si no hay token (ej. petición a /login)
    return next(req);
};
