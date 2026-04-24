import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { inject } from '@angular/core';
import { NotificationService } from '../services/notification';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notificationService = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage: string;

      if (error.status === 0) {
        errorMessage = 'No hay conexión con el servidor. Verifica tu red o intenta más tarde.';
        notificationService.showError(errorMessage);
      } else {
        errorMessage = `Error ${error.status}: ${error.error?.error ?? error.message}`;
        // En un futuro podemos notificar también errores 4xx o 5xx
        // notificationService.showError(errorMessage);
      }

      console.error(`[HTTP Error] ${errorMessage}`);
      return throwError(() => new Error(errorMessage));
    })
  );
};
