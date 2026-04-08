import { Component, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { SearchForm } from '../../../models/search-form.interface';

@Component({
  selector: 'app-hero-search-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './hero-search-form.html',
  styleUrl: './hero-search-form.css',
})
export class HeroSearchFormComponent {
  readonly search = output<SearchForm>();

  form = signal<SearchForm>({
    location: '',
    checkIn: '',
    checkOut: '',
    guests: null,
  });

  updateField(field: keyof SearchForm, value: string | number | null): void {
    this.form.update(current => ({ ...current, [field]: value }));
  }

  onSearch(): void {
    this.search.emit(this.form());
  }
}
