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
}