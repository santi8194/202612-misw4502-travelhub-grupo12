export interface SearchRequest {
  ciudad: string;
  estado_provincia: string;
  pais: string;
  fecha_inicio: string;   // YYYY-MM-DD
  fecha_fin: string;      // YYYY-MM-DD
  huespedes: number;
}
