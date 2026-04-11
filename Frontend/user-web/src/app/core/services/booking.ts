import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { HoldRequest, HoldResponse } from '../../models/hold.interface';

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `http://localhost:5001/api/reserva`;
  private readonly catalogUrl = `http://localhost:8005/catalog`;

  createHold(request: HoldRequest): Observable<HoldResponse> {
    console.info('[BookingService] POST', `${this.apiUrl}`, request);
    return this.http.post<HoldResponse>(`${this.apiUrl}`, request).pipe(
      tap((response) => console.info('[BookingService] createHold success', response)),
      catchError((error) => {
        console.error('[BookingService] createHold error', { request, error });
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
}