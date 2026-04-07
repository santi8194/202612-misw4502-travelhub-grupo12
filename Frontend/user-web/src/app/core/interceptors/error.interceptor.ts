import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage: string;

      if (error.status === 0) {
        errorMessage = 'No hay conexión con el servidor';
      } else {
        errorMessage = `Error ${error.status}: ${error.error?.error ?? error.message}`;
      }

      console.error(`[HTTP Error] ${errorMessage}`);
      return throwError(() => new Error(errorMessage));
    })
  );
};
