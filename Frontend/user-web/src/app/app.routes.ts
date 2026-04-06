import { Routes } from '@angular/router';
import { GuestsPage } from './pages/guests-page/guests-page';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'booking',
    pathMatch: 'full'
  },
  {
    path: 'booking',
    component: GuestsPage
  }
];
