export interface Coordenadas {
  lat: number;
  lon: number;
}

export interface Hospedaje {
  id_propiedad: string;
  id_categoria: string;
  propiedad_nombre: string;
  categoria_nombre: string;
  imagen_principal_url: string;
  amenidades_destacadas: string[];
  estrellas: number;
  rating_promedio: number;
  ciudad: string;
  estado_provincia: string;
  pais: string;
  coordenadas: Coordenadas;
  capacidad_pax: number;
  precio_base: string;
  moneda: string;
  es_reembolsable: boolean;
}

export interface SearchResultsResponse {
  resultados: Hospedaje[];
  total: number;
}
