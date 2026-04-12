import { Injectable, signal } from '@angular/core';

export interface NotificationState {
  show: boolean;
  message: string;
  type: 'error' | 'success'; 
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  readonly state = signal<NotificationState>({ show: false, message: '', type: 'error' });

  showError(message: string): void {
    this.state.set({ show: true, message, type: 'error' });
    setTimeout(() => this.hide(), 5000);
  }

  showSuccess(message: string): void {
    this.state.set({ show: true, message, type: 'success' });
    setTimeout(() => this.hide(), 5000);
  }

  hide(): void {
    this.state.update(s => ({ ...s, show: false }));
  }
}
