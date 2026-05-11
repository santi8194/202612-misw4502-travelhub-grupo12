import { Component } from '@angular/core';
import { environment } from '../../../../environments/environment';
import { TranslatePipe } from '../../pipes/translate.pipe';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './footer.html',
  styleUrl: './footer.css',
})
export class FooterComponent {
  get appVersion(): string {
    return environment.version;
  }
}
