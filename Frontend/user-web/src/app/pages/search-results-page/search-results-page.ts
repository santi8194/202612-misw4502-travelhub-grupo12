import { Component, computed, signal } from '@angular/core';
import { HeaderComponent } from '../../shared/components/header/header';
import { FooterComponent } from '../../shared/components/footer/footer';
import { HospedajeCardComponent } from '../../shared/components/hospedaje-card/hospedaje-card';
import { Hospedaje } from '../../models/hospedaje.interface';

const MOCK_HOSPEDAJES: Hospedaje[] = [
  {
    id_propiedad: '550e8400-e29b-41d4-a716-446655440000',
    id_categoria: '550e8400-e29b-41d4-a716-446655440010',
    propiedad_nombre: 'Hotel',
    categoria_nombre: 'Bordeaux Getaway',
    imagen_principal_url: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop',
    amenidades_destacadas: ['Wifi', 'Cocina', 'Cuarto de ropa', 'Piscina'],
    estrellas: 5,
    rating_promedio: 5.0,
    ciudad: 'Bordeaux',
    estado_provincia: 'Nouvelle-Aquitaine',
    pais: 'Francia',
    coordenadas: { lat: 44.8378, lon: -0.5792 },
    capacidad_pax: 2,
    precio_base: '75.00',
    moneda: 'USD',
    es_reembolsable: true,
  },
  {
    id_propiedad: '550e8400-e29b-41d4-a716-446655440001',
    id_categoria: '550e8400-e29b-41d4-a716-446655440010',
    propiedad_nombre: 'Hotel',
    categoria_nombre: 'Charming Waterfront Condo',
    imagen_principal_url: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&auto=format&fit=crop',
    amenidades_destacadas: ['Wifi', 'Cocina', 'Cuarto de ropa', 'Terraza'],
    estrellas: 5,
    rating_promedio: 5.0,
    ciudad: 'Bordeaux',
    estado_provincia: 'Nouvelle-Aquitaine',
    pais: 'Francia',
    coordenadas: { lat: 44.8412, lon: -0.5736 },
    capacidad_pax: 4,
    precio_base: '80.00',
    moneda: 'USD',
    es_reembolsable: false,
  },
  {
    id_propiedad: '550e8400-e29b-41d4-a716-446655440002',
    id_categoria: '550e8400-e29b-41d4-a716-446655440010',
    propiedad_nombre: 'Hotel',
    categoria_nombre: 'Historic City Center Home',
    imagen_principal_url: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&auto=format&fit=crop',
    amenidades_destacadas: ['Wifi', 'Cocina', 'Cuarto de ropa', 'Jardín'],
    estrellas: 4,
    rating_promedio: 4.5,
    ciudad: 'Bordeaux',
    estado_provincia: 'Nouvelle-Aquitaine',
    pais: 'Francia',
    coordenadas: { lat: 44.8356, lon: -0.5805 },
    capacidad_pax: 3,
    precio_base: '50.00',
    moneda: 'USD',
    es_reembolsable: true,
  },
];

@Component({
  selector: 'app-search-results-page',
  standalone: true,
  imports: [HeaderComponent, FooterComponent, HospedajeCardComponent],
  templateUrl: './search-results-page.html',
  styleUrl: './search-results-page.css',
})
export class SearchResultsPage {
  readonly hospedajes = signal<Hospedaje[]>(MOCK_HOSPEDAJES);

  readonly ciudadBusqueda = computed(() => {
    const primero = this.hospedajes()[0];
    return primero ? primero.ciudad : '';
  });

  readonly totalResultados = computed(() => this.hospedajes().length);
}
