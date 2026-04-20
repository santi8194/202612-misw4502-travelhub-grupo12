import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Hospedaje } from '../../../models/hospedaje.interface';

const MAX_AMENIDADES_VISIBLES = 3;

@Component({
  selector: 'app-hospedaje-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './hospedaje-card.html',
  styleUrl: './hospedaje-card.css',
})
export class HospedajeCardComponent {
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
}
