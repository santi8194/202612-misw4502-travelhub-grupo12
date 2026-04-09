import { Component, output, signal, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { Subject, of } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, filter, catchError, map } from 'rxjs/operators';
import { SearchForm } from '../../../models/search-form.interface';
import { SearchService } from '../../../core/services/search';
import { DestinationItem } from '../../../models/destination.interface';

@Component({
  selector: 'app-hero-search-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './hero-search-form.html',
  styleUrl: './hero-search-form.css',
})
export class HeroSearchFormComponent {
  private readonly searchService = inject(SearchService);
  readonly search = output<SearchForm>();

  form = signal<SearchForm>({
    location: '',
    checkIn: '',
    checkOut: '',
    guests: null,
  });

  private locationQuerySubject = new Subject<string>();

  // RxJS pipeline for autocomplete
  private locationSuggestions$ = this.locationQuerySubject.pipe(
    filter(query => query.length >= 3 || query.length === 0),
    debounceTime(300),
    distinctUntilChanged(),
    switchMap(query => {
      if (query.length === 0) return of([]);
      return this.searchService.autocompleteDestinations(query).pipe(
        map(res => res.results),
        catchError(() => of([]))
      );
    })
  );

  // Expose as a signal for the template
  suggestions = toSignal(this.locationSuggestions$, { initialValue: [] });

  updateField(field: keyof SearchForm, value: string | number | null): void {
    this.form.update(current => ({ ...current, [field]: value }));
  }

  onLocationInput(value: string): void {
    this.updateField('location', value);
    this.locationQuerySubject.next(value);
  }

  selectDestination(dest: DestinationItem): void {
    const locationString = [dest.ciudad, dest.estado_provincia, dest.pais]
      .filter(Boolean)
      .join(', ');
    this.updateField('location', locationString);
    this.locationQuerySubject.next(''); // Clear dropdown
  }

  onSearch(): void {
    this.search.emit(this.form());
  }
}

