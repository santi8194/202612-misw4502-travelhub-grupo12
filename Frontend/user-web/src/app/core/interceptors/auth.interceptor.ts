import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const session = authService.getCurrentSession();

  if (session?.accessToken) {
    const authReq = req.clone({
      setHeaders: { Authorization: `Bearer ${session.accessToken}` },
    });
    return next(authReq);
  }

  return next(req);
};
