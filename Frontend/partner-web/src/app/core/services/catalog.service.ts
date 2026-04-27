import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface TarifaVO {
    monto: string;
    moneda: string;
    cargo_servicio: string;
}

export interface CategoriaApi {
    id_categoria: string;
    nombre_comercial: string;
    precio_base: TarifaVO;
    capacidad_pax: number;
    codigo_mapeo_pms?: string;
}

export interface CategoriasResponse {
    id_propiedad: string;
    total_categorias: number;
    categorias: CategoriaApi[];
}

export interface PricingResponse {
    id_categoria: string;
    nombre_comercial: string;
    tarifa_base: TarifaVO | null;
    tarifa_fin_de_semana: TarifaVO | null;
    tarifa_temporada_alta: TarifaVO | null;
}

export interface PricingUpdate {
    tarifa_base_monto: string;
    moneda: string;
    cargo_servicio: string;
    tarifa_fin_de_semana_monto: string | null;
    tarifa_temporada_alta_monto: string | null;
}

export interface TemporadaApi {
    id_temporada: string;
    nombre: string;
    fecha_inicio: string;   // "YYYY-MM-DD"
    fecha_fin: string;      // "YYYY-MM-DD"
    porcentaje: number;
}

export interface TemporadasResponse {
    id_propiedad: string;
    temporadas: TemporadaApi[];
}

export interface CreateTemporadaBody {
    nombre: string;
    fecha_inicio: string;
    fecha_fin: string;
    porcentaje: number;
}

@Injectable({
    providedIn: 'root'
})
export class CatalogService {
    private readonly base = environment.catalogApiUrl;

    constructor(private http: HttpClient) {}

    getCategorias(idPropiedad: string): Observable<CategoriasResponse> {
        return this.http.get<CategoriasResponse>(
            `${this.base}/properties/${idPropiedad}/categories`
        );
    }

    getPricing(idPropiedad: string, idCategoria: string): Observable<PricingResponse> {
        return this.http.get<PricingResponse>(
            `${this.base}/properties/${idPropiedad}/categories/${idCategoria}/pricing`
        );
    }

    updatePricing(idPropiedad: string, idCategoria: string, body: PricingUpdate): Observable<unknown> {
        return this.http.put(
            `${this.base}/properties/${idPropiedad}/categories/${idCategoria}/pricing`,
            body
        );
    }

    getTemporadas(idPropiedad: string): Observable<TemporadasResponse> {
        return this.http.get<TemporadasResponse>(
            `${this.base}/properties/${idPropiedad}/seasons`
        );
    }

    createTemporada(idPropiedad: string, body: CreateTemporadaBody): Observable<TemporadaApi> {
        return this.http.post<TemporadaApi>(
            `${this.base}/properties/${idPropiedad}/seasons`,
            body
        );
    }

    deleteTemporada(idPropiedad: string, idTemporada: string): Observable<unknown> {
        return this.http.delete(
            `${this.base}/properties/${idPropiedad}/seasons/${idTemporada}`
        );
    }
}
