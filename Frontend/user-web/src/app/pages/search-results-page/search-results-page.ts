import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { switchMap, catchError, map } from 'rxjs/operators';
import { of } from 'rxjs';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HospedajeCardComponent } from '../../shared/components/hospedaje-card/hospedaje-card';
import { Hospedaje } from '../../models/hospedaje.interface';
import { SearchService } from '../../core/services/search';

@Component({
  selector: 'app-search-results-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, HospedajeCardComponent, RouterLink],
  templateUrl: './search-results-page.html',
  styleUrl: './search-results-page.css',
})
export class SearchResultsPage {
  private readonly route = inject(ActivatedRoute);
  private readonly searchService = inject(SearchService);

  readonly loading = signal<boolean>(true);

  private readonly results$ = this.route.queryParams.pipe(
    switchMap(params => {
      const ciudad = params['ciudad'] ?? '';
      if (!ciudad) {
        this.loading.set(false);
        return of([]);
      }

      this.loading.set(true);
      return this.searchService.searchHospedajes({
        ciudad,
        estado_provincia: params['estado_provincia'] ?? '',
        pais: params['pais'] ?? '',
        fecha_inicio: params['fecha_inicio'] ?? '',
        fecha_fin: params['fecha_fin'] ?? '',
        huespedes: Number(params['huespedes']) || 1,
      }).pipe(
        map(res => {
          this.loading.set(false);
          return res.resultados;
        }),
        catchError(() => {
          this.loading.set(false);
          return of([]);
        }),
      );
    }),
  );

  readonly hospedajes = toSignal(this.results$, { initialValue: [] as Hospedaje[] });

  readonly ciudadBusqueda = computed(() => {
    const primero = this.hospedajes()?.[0];
    return primero ? primero.ciudad : (this.route.snapshot.queryParams['ciudad'] ?? '');
  });

  readonly totalResultados = computed(() => this.hospedajes()?.length ?? 0);
}
