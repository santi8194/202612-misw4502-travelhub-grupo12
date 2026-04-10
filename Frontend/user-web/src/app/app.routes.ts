import { Routes } from '@angular/router';

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
    path: 'booking/:id_reserva',
    loadComponent: () =>
      import('./pages/booking-cart-page/booking-cart-page').then(m => m.BookingCartPage),
  },
  {
    path: 'booking',
    loadComponent: () =>
      import('./pages/booking-cart-page/booking-cart-page').then(m => m.BookingCartPage),
  },
];
