import { Routes } from '@angular/router';
import { ExistingSessionRedirectPage } from './pages/existing-session-redirect-page/existing-session-redirect-page';
import { ProcessingReservationPage } from './pages/processing-reservation-page/processing-reservation-page';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: 'auth/registro',
    loadComponent: () =>
      import('./pages/auth-register-page/auth-register-page').then(m => m.AuthRegisterPage),
  },
  {
    path: 'auth/confirmar',
    loadComponent: () =>
      import('./pages/auth-confirm-page/auth-confirm-page').then(m => m.AuthConfirmPage),
  },
  {
    path: 'auth/login',
    loadComponent: () =>
      import('./pages/auth-login-page/auth-login-page').then(m => m.AuthLoginPage),
  },
  {
    path: '',
    loadComponent: () =>
      import('./pages/home-page/home-page').then(m => m.HomePage),
  },
  {
    path: 'resultados',
    loadComponent: () =>
      import('./pages/search-results-page/search-results-page').then(m => m.SearchResultsPage),
  },
  {
    path: 'property/:property_id',
    loadComponent: () =>
      import('./pages/property-detail-page/property-detail-page').then(m => m.PropertyDetailPage),
  },
  {
    path: 'category/:category_id',
    loadComponent: () =>
      import('./pages/room-detail-page/room-detail-page').then(m => m.RoomDetailPage),
  },
  {
    path: 'booking/:id_reserva/payment',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/payment-page/payment-page').then(m => m.PaymentPage),
  },
  {
    path: 'booking/:id_reserva/confirm-reservation',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/confirm-reservation-page/confirm-reservation-page').then(m => m.ConfirmReservationPage),
  },
  {
    path: 'booking/:id_reserva/processing-reservation',
    canActivate: [authGuard],
    loadComponent: () => Promise.resolve(ProcessingReservationPage),
  },
  {
    path: 'booking/:id_reserva',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/booking-cart-page/booking-cart-page').then(m => m.BookingCartPage),
  },
  {
    path: 'existing-session-redirect',
    loadComponent: () => Promise.resolve(ExistingSessionRedirectPage),
  },
  {
    path: 'mis-reservas',
    loadComponent: () =>
      import('./pages/my-reservations-page/my-reservations-page').then(m => m.MyReservationsPage),
  },
  {
    path: 'mis-reservas/:id_reserva',
    loadComponent: () =>
      import('./pages/my-reservations-page/my-reservations-page').then(m => m.MyReservationsPage),
  },
];
