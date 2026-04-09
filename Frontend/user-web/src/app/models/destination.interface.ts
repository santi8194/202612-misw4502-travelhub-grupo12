export interface DestinationItem {
  ciudad: string;
  estado_provincia: string;
  pais: string;
}

export interface DestinationResponse {
  results: DestinationItem[];
}
