import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { SearchStateService } from '../../../core/services/search-state';

@Component({
  selector: 'app-compact-search-bar',
  standalone: true,
  imports: [],
  templateUrl: './compact-search-bar.html',
  styleUrl: './compact-search-bar.css',
})
export class CompactSearchBarComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly searchStateService = inject(SearchStateService);

  private readonly params = toSignal(this.route.queryParams, { requireSync: true });

  readonly cityLabel = computed(() => this.params()['ciudad'] ?? '');

  readonly datesLabel = computed(() => {
    const p = this.params();
    if (!p['fecha_inicio'] || !p['fecha_fin']) return '';
    return this.formatDateRange(p['fecha_inicio'], p['fecha_fin']);
  });

  readonly guestsLabel = computed(() => {
    const g = Number(this.params()['huespedes']) || 1;
    return `${g} huésped${g !== 1 ? 'es' : ''}`;
  });

  onEditSearch(): void {
    if (!this.cityLabel()) return;
    const p = this.params();
    this.searchStateService.set({
      location: [p['ciudad'], p['estado_provincia'], p['pais']].filter(Boolean).join(', '),
      checkIn: p['fecha_inicio'] ?? '',
      checkOut: p['fecha_fin'] ?? '',
      guests: Number(p['huespedes']) || 1,
      selectedDestination: {
        ciudad: p['ciudad'] ?? '',
        estado_provincia: p['estado_provincia'] ?? '',
        pais: p['pais'] ?? '',
      },
    });
    this.router.navigate(['/']);
  }

  private formatDateRange(checkIn: string, checkOut: string): string {
    const fmt = new Intl.DateTimeFormat('es', { month: 'short', day: 'numeric' });
    const start = new Date(checkIn + 'T00:00:00');
    const end = new Date(checkOut + 'T00:00:00');
    const startStr = fmt.format(start);
    if (start.getMonth() === end.getMonth()) {
      return `${startStr}-${end.getDate()}`;
    }
    const endStr = new Intl.DateTimeFormat('es', { month: 'short', day: 'numeric' }).format(end);
    return `${startStr} - ${endStr}`;
  }
}
