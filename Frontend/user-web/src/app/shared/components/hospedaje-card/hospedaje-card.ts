import { Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Hospedaje } from '../../../models/hospedaje.interface';

const MAX_AMENIDADES_VISIBLES = 3;

@Component({
  selector: 'app-hospedaje-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './hospedaje-card.html',
  styleUrl: './hospedaje-card.css',
})
export class HospedajeCardComponent {
  hospedaje = input.required<Hospedaje>();

  amenidadesVisibles = computed(() =>
    this.hospedaje().amenidades_destacadas.slice(0, MAX_AMENIDADES_VISIBLES)
  );

  amenidadesRestantes = computed(() =>
    Math.max(0, this.hospedaje().amenidades_destacadas.length - MAX_AMENIDADES_VISIBLES)
  );
}
