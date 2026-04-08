import { Component } from '@angular/core';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HeroSearchFormComponent } from '../../shared/components/hero-search-form/hero-search-form';
import { SearchForm } from '../../models/search-form.interface';

@Component({
  selector: 'app-home-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, HeroSearchFormComponent],
  templateUrl: './home-page.html',
  styleUrl: './home-page.css',
})
export class HomePage {
  onSearch(form: SearchForm): void {
    // Hito 1: sin conexión al backend
    // Hito 2: navegar a /resultados con los query params
    console.log('[HomePage] Search submitted:', form);
  }
}
