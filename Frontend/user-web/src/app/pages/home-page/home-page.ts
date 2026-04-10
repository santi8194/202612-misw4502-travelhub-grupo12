import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
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
  private readonly router = inject(Router);

  onSearch(form: SearchForm): void {
    if (!form.selectedDestination) return;

    this.router.navigate(['/resultados'], {
      queryParams: {
        ciudad: form.selectedDestination.ciudad,
        estado_provincia: form.selectedDestination.estado_provincia,
        pais: form.selectedDestination.pais,
        fecha_inicio: form.checkIn,
        fecha_fin: form.checkOut,
        huespedes: form.guests ?? 1,
      },
    });
  }
}
