import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, tap, throwError } from 'rxjs';
import { HoldRequest, HoldResponse } from '../../models/hold.interface';

interface CreateBookingRequest {
  id_usuario: string;
  id_categoria: string;
  fecha_check_in: string;
  fecha_check_out: string;
  ocupacion: {
    adultos: number;
    ninos: number;
    infantes: number;
  };
}

interface CreateBookingResponse {
  id_reserva: string;
  mensaje?: string;
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `http://localhost:5001/api/reserva`;
  private readonly catalogUrl = `http://localhost:8005/catalog`;

  createHold(request: HoldRequest): Observable<HoldResponse> {
    const mappedRequest: CreateBookingRequest = {
      id_usuario: crypto.randomUUID(),
      id_categoria: String(request.categoryId),
      fecha_check_in: request.checkIn,
      fecha_check_out: request.checkOut,
      ocupacion: {
        adultos: request.guests,
        ninos: 0,
        infantes: 0,
      },
    };

    console.info('[BookingService] POST', `${this.apiUrl}`, mappedRequest);
    return this.http.post<CreateBookingResponse>(`${this.apiUrl}`, mappedRequest).pipe(
      tap((response) => console.info('[BookingService] createHold success', response)),
      map((response) => {
        if (!response?.id_reserva) {
          throw new Error('Backend did not return id_reserva');
        }

        // Backend create endpoint does not provide an expiration timestamp.
        return {
          id: response.id_reserva,
          expiresAt: 0,
        };
      }),
      catchError((error) => {
        console.error('[BookingService] createHold error', { request: mappedRequest, error });
        return throwError(() => error);
      })
    );
  }

  getBookingById(idReserva: string): Observable<any> {
    const url = `${this.apiUrl}/${idReserva}`;
    console.info('[BookingService] GET', url);
    return this.http.get<any>(url).pipe(
      tap((response) => console.info('[BookingService] getBookingById success', response)),
      catchError((error) => {
        console.error('[BookingService] getBookingById error', { idReserva, error });
        return throwError(() => error);
      })
    );
  }

  getCatalogByCategoryId(idCategoria: string): Observable<any> {
    const url = `${this.catalogUrl}/properties/by-category/${idCategoria}`;
    console.info('[BookingService] GET', url);
    return this.http.get<any>(url).pipe(
      tap((response) => console.info('[BookingService] getCatalogByCategoryId success', response)),
      catchError((error) => {
        console.error('[BookingService] getCatalogByCategoryId error', { idCategoria, error });
        return throwError(() => error);
      })
    );
  }

  getPropertyById(propertyId: string): Observable<any> {
    const url = `${this.catalogUrl}/properties/${propertyId}`;
    console.info('[BookingService] GET', url);
    return this.http.get<any>(url).pipe(
      tap((response) => console.info('[BookingService] getPropertyById success', response)),
      catchError((error) => {
        console.error('[BookingService] getPropertyById error', { propertyId, error });
        return throwError(() => error);
      })
    );
  }

  getPropertyCategories(propertyId: string): Observable<any> {
    const url = `${this.catalogUrl}/properties/${propertyId}/categories`;
    console.info('[BookingService] GET', url);
    return this.http.get<any>(url).pipe(
      tap((response) => console.info('[BookingService] getPropertyCategories success', response)),
      catchError((error) => {
        console.error('[BookingService] getPropertyCategories error', { propertyId, error });
        return throwError(() => error);
      })
    );
  }

  createBooking(request: CreateBookingRequest): Observable<CreateBookingResponse> {
    console.info('[BookingService] POST', `${this.apiUrl}`, request);
    return this.http.post<CreateBookingResponse>(`${this.apiUrl}`, request).pipe(
      tap((response) => console.info('[BookingService] createBooking success', response)),
      catchError((error) => {
        console.error('[BookingService] createBooking error', { request, error });
        return throwError(() => error);
      })
    );
  }
}