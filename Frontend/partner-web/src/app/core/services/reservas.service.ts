import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ReservaPorPropiedadApi {
    id_reserva: string;
    id_usuario: string | null;
    id_propiedad: string;
    id_categoria: string | null;
    habitacion: string | null;
    estado: string | null;
    fecha_check_in: string | null;
    fecha_check_out: string | null;
    huespedes: number;
    pago: string | null;
    total: number | null;
}

export interface ReservaDetalleApi {
    id_reserva: string;
    id_usuario: string | null;
    id_categoria: string | null;
    codigo_confirmacion_ota: string | null;
    codigo_localizador_pms: string | null;
    estado: string | null;
    fecha_check_in: string | null;
    fecha_check_out: string | null;
    ocupacion: {
        adultos: number;
        ninos: number;
        infantes: number;
    } | null;
    fecha_creacion: string | null;
    fecha_actualizacion: string | null;
}

export interface ReservaTimelineItemApi {
    id_log: string;
    tipo_mensaje: string;
    accion: string;
    payload: Record<string, unknown> | null;
    fecha_registro: string | null;
}

export interface ReservaTimelineApi {
    id_reserva: string;
    id_instancia_saga: string;
    id_flujo: string;
    version_ejecucion: number;
    estado_global: string;
    paso_actual: number;
    total_eventos: number;
    timeline: ReservaTimelineItemApi[];
}

@Injectable({
    providedIn: 'root'
})
export class ReservasService {
    private readonly base = environment.bookingApiUrl;

    constructor(private http: HttpClient) {}

    getReservasPorPropiedad(idPropiedad: string): Observable<ReservaPorPropiedadApi[]> {
        return this.http.get<ReservaPorPropiedadApi[]>(
            `${this.base}/reserva/propiedad/${encodeURIComponent(idPropiedad)}`
        );
    }

    getReservaPorId(idReserva: string): Observable<ReservaDetalleApi> {
        return this.http.get<ReservaDetalleApi>(
            `${this.base}/reserva/${encodeURIComponent(idReserva)}`
        );
    }

    getTimelinePorReserva(idReserva: string): Observable<ReservaTimelineApi> {
        return this.http.get<ReservaTimelineApi>(
            `${this.base}/reserva/${encodeURIComponent(idReserva)}/timeline`
        );
    }
}