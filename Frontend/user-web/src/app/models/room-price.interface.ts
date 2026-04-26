export interface CalculateRoomPriceRequest {
  id_categoria: string;
  fecha_inicio: string;
  fecha_fin: string;
  pais_usuario: string;
}

export interface RoomPriceResponse {
  precio_por_noche: number;
  noches: number;
  subtotal: number;
  impuestos: number;
  cargo_servicio: number;
  total: number;
  moneda: string;
  simbolo_moneda: string;
  tipo_tarifa: string;
  impuesto_nombre: string;
}
