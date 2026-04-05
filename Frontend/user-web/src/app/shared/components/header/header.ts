import { Component } from '@angular/core';
import { SearchBarComponent } from '../search-bar/search-bar';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [SearchBarComponent],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class HeaderComponent {

}
