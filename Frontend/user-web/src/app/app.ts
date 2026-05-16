import { Component, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NotificationComponent } from './shared/components/notification/notification';
import { I18nService } from './core/i18n/i18n.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NotificationComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private readonly i18n = inject(I18nService);
  protected readonly title = signal('user-web');
}
