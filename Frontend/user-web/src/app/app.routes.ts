import { Routes } from '@angular/router';
import { ExistingSessionRedirectPage } from './pages/existing-session-redirect-page/existing-session-redirect-page';
import { ProcessingReservationPage } from './pages/processing-reservation-page/processing-reservation-page';

export const routes: Routes = [
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
    loadComponent: () =>
      import('./pages/payment-page/payment-page').then(m => m.PaymentPage),
  },
  {
    path: 'booking/:id_reserva/confirm-reservation',
    loadComponent: () =>
      import('./pages/confirm-reservation-page/confirm-reservation-page').then(m => m.ConfirmReservationPage),
  },
  {
    path: 'booking/:id_reserva/processing-reservation',
    loadComponent: () => Promise.resolve(ProcessingReservationPage),
  },
  {
    path: 'booking/:id_reserva',
    loadComponent: () =>
      import('./pages/booking-cart-page/booking-cart-page').then(m => m.BookingCartPage),
  },
  {
    path: 'existing-session-redirect',
    loadComponent: () => Promise.resolve(ExistingSessionRedirectPage),
  },
];
