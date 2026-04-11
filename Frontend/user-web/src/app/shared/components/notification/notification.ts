import { Component, inject } from '@angular/core';
import { NotificationService } from '../../../core/services/notification';

@Component({
  selector: 'app-notification',
  standalone: true,
  template: `
    @if (notificationService.state().show) {
      <div 
        class="notification-toast flex items-start gap-4 p-4 shadow-lg rounded-xl z-50 fixed top-8 right-8 cursor-pointer transition-all duration-300 transform w-96 max-w-full"
        [class.notification-error]="notificationService.state().type === 'error'"
        [class.notification-success]="notificationService.state().type === 'success'"
        (click)="notificationService.hide()">
        
        <div class="flex-shrink-0 pt-0.5">
          @if (notificationService.state().type === 'error') {
            <svg class="w-6 h-6 outline-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          }
        </div>

        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium leading-relaxed m-0 text-inherit">
            {{ notificationService.state().message }}
          </p>
        </div>

        <button 
          title="Cerrar notificación"
          class="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity p-0.5 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-1 h-5 w-5 flex items-center justify-center cursor-pointer bg-transparent border-none">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    }
  `,
  styleUrl: './notification.css'
})
export class NotificationComponent {
  readonly notificationService = inject(NotificationService);
}
