import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { HoldRequest, HoldResponse } from '../../models/hold.interface';

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiBaseUrl}/booking`;
  private readonly catalogUrl = `${environment.apiBaseUrl}/catalog`;

  createHold(request: HoldRequest): Observable<HoldResponse> {
    return this.http.post<HoldResponse>(`${this.apiUrl}/hold`, request);
  }

  getBookingById(idReserva: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${idReserva}`);
  }

  getCatalogByCategoryId(idCategoria: string): Observable<any> {
    return this.http.get<any>(`${this.catalogUrl}/properties?category=${idCategoria}`);
  }
}