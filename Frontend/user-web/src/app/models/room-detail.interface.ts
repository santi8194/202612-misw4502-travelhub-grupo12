export interface RoomDetailResponse {
  propiedad: RoomPropertyInfo;
  categoria: RoomCategoryInfo;
  amenidades: RoomAmenity[];
  galeria: RoomMedia[];
  rating_promedio: number;
  total_resenas: number;
  resenas: RoomReview[];
}

export interface RoomPropertyInfo {
  id_propiedad: string;
  nombre: string;
  estrellas: number;
  ubicacion: {
    ciudad: string;
    estado_provincia: string;
    pais: string;
    coordenadas: { lat: number; lng: number };
  };
  porcentaje_impuesto: string;
}

export interface RoomCategoryInfo {
  id_categoria: string;
  nombre_comercial: string;
  descripcion: string;
  precio_base: {
    monto: string;
    moneda: string;
    cargo_servicio: string;
  };
  capacidad_pax: number;
  politica_cancelacion: {
    dias_anticipacion: number;
    porcentaje_penalidad: string;
  };
}

export interface RoomAmenity {
  id_amenidad: string;
  nombre: string;
  icono: string;
}

export interface RoomMedia {
  id_media: string;
  url_full: string;
  tipo: string;
  orden: number;
}

export interface RoomReview {
  id_resena: string;
  id_usuario: string;
  nombre_autor: string;
  avatar_url: string;
  calificacion: number;
  comentario: string;
  fecha_creacion: string;
}
