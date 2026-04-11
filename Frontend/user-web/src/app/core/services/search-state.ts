import { Injectable, signal } from '@angular/core';
import { SearchForm } from '../../models/search-form.interface';

@Injectable({ providedIn: 'root' })
export class SearchStateService {
  readonly currentSearch = signal<SearchForm | null>(null);

  set(form: SearchForm): void {
    this.currentSearch.set(form);
  }

  reset(): void {
    this.currentSearch.set(null);
  }
}
