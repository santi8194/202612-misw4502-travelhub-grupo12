import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'booking',
    pathMatch: 'full'
  },
  {
    path: 'booking',
    loadComponent: () =>
      import('./pages/guests-page/guests-page').then(m => m.GuestsPage),
  }
];
