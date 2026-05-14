import { Component, computed, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Hospedaje } from '../../../models/hospedaje.interface';
import { TranslatePipe } from '../../pipes/translate.pipe';
import { I18nService } from '../../../core/i18n/i18n.service';

const MAX_AMENIDADES_VISIBLES = 3;

@Component({
  selector: 'app-hospedaje-card',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslatePipe],
  templateUrl: './hospedaje-card.html',
  styleUrl: './hospedaje-card.css',
})
export class HospedajeCardComponent {
  private readonly i18n = inject(I18nService);

  hospedaje = input.required<Hospedaje>();

  searchParams = input<{ fecha_inicio: string; fecha_fin: string; huespedes: number }>({
    fecha_inicio: '',
    fecha_fin: '',
    huespedes: 1,
  });

  categoryLink = computed(() => `/category/${this.hospedaje().id_categoria}`);

  categoryQueryParams = computed(() => ({
    fecha_inicio: this.searchParams().fecha_inicio,
    fecha_fin: this.searchParams().fecha_fin,
    huespedes: this.searchParams().huespedes,
  }));

  amenidadesVisibles = computed(() =>
    this.hospedaje().amenidades_destacadas.slice(0, MAX_AMENIDADES_VISIBLES)
  );

  amenidadesRestantes = computed(() =>
    Math.max(0, this.hospedaje().amenidades_destacadas.length - MAX_AMENIDADES_VISIBLES)
  );

  readonly translatedPropertyName = computed(() => this.translateBackendLabel(this.hospedaje().propiedad_nombre));
  readonly translatedCategoryName = computed(() => this.translateBackendLabel(this.hospedaje().categoria_nombre));

  private translateBackendLabel(value: string): string {
    const normalized = value.trim().toLowerCase();
    const key = this.backendLabelKeyMap[normalized];
    if (!key) {
      return value;
    }
    return this.i18n.translate(key);
  }

  private readonly backendLabelKeyMap: Record<string, string> = {
    finca: 'propertyType.finca',
    hotel: 'propertyType.hotel',
    hostal: 'propertyType.hostal',
    apartamento: 'propertyType.apartment',
    apartahotel: 'propertyType.aparthotel',
    casa: 'propertyType.house',
    cabaña: 'propertyType.cabin',
    cabana: 'propertyType.cabin',
  };
}
