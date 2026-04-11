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
    path: 'booking',
    loadComponent: () =>
      import('./pages/guests-page/guests-page').then(m => m.GuestsPage),
  },
];
