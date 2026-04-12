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
    path: 'property/:property_id',
    loadComponent: () =>
      import('./pages/property-detail-page/property-detail-page').then(m => m.PropertyDetailPage),
  },
  {
    path: 'booking/:id_reserva',
    loadComponent: () =>
      import('./pages/booking-cart-page/booking-cart-page').then(m => m.BookingCartPage),
  },
];
