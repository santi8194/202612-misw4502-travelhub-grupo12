import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    // Dejar pasar a la ruta seleccionada
    if (authService.isAuthenticated()) {
        return true;
    }

    // Cortar la navegación y enviar a Login
    router.navigate(['/login']);
    return false;
};
