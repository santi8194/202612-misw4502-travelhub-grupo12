import { Component, output, signal, inject, computed } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { Subject, of } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, filter, catchError, map } from 'rxjs/operators';
import { SearchForm } from '../../../models/search-form.interface';
import { SearchService } from '../../../core/services/search';
import { SearchStateService } from '../../../core/services/search-state';
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
  private readonly searchStateService = inject(SearchStateService);
  readonly search = output<SearchForm>();

  form = signal<SearchForm>(
    this.searchStateService.currentSearch() ?? {
      location: '',
      checkIn: '',
      checkOut: '',
      guests: 1,
      selectedDestination: undefined,
    }
  );

  formErrors = signal({
    location: false,
    dates: false,
    guests: false,
  });

  minCheckInDate = computed(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });

  maxDate = computed(() => {
    const nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    return nextYear.toISOString().split('T')[0];
  });

  minCheckOutDate = computed(() => {
    const checkIn = this.form().checkIn;
    return checkIn ? checkIn : this.minCheckInDate();
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
    if (field === 'location') this.formErrors.update(e => ({ ...e, location: false }));
    if (field === 'checkIn' || field === 'checkOut') this.formErrors.update(e => ({ ...e, dates: false }));
    if (field === 'guests') this.formErrors.update(e => ({ ...e, guests: false }));
  }

  onLocationInput(value: string): void {
    this.updateField('location', value);
    this.locationQuerySubject.next(value);
  }

  selectDestination(dest: DestinationItem): void {
    const locationString = [dest.ciudad, dest.estado_provincia, dest.pais]
      .filter(Boolean)
      .join(', ');
    this.form.update(current => ({
      ...current,
      location: locationString,
      selectedDestination: dest,
    }));
    this.locationQuerySubject.next(''); // Clear dropdown
  }

  increaseGuests(): void {
    const current = this.form().guests || 0;
    this.updateField('guests', current + 1);
  }

  decreaseGuests(): void {
    const current = this.form().guests || 0;
    if (current > 1) {
      this.updateField('guests', current - 1);
    }
  }

  onSearch(): void {
    const f = this.form();
    const locationValid = !!f.location;
    const datesValid = !!f.checkIn && !!f.checkOut;
    const guestsValid = !!f.guests && f.guests > 0;

    this.formErrors.set({
      location: !locationValid,
      dates: !datesValid,
      guests: !guestsValid
    });

    if (locationValid && datesValid && guestsValid) {
      this.search.emit(f);
    }
  }
}

