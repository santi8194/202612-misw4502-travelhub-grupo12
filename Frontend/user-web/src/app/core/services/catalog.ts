import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { RoomDetailResponse } from '../../models/room-detail.interface';
import { CalculateRoomPriceRequest, RoomPriceResponse } from '../../models/room-price.interface';

@Injectable({ providedIn: 'root' })
export class CatalogService {
  private readonly http = inject(HttpClient);
  private readonly catalogUrl = environment.catalogApiUrl;

  getCategoryViewDetail(categoryId: string, lang: 'es' | 'en' = 'es'): Observable<RoomDetailResponse> {
    const url = `${this.catalogUrl}/categories/${categoryId}/view-detail`;
    console.info('[CatalogService] GET', url);
    const params = new HttpParams().set('lang', lang);
    return this.http.get<RoomDetailResponse>(url, { params }).pipe(
      tap(response => console.info('[CatalogService] getCategoryViewDetail success', response)),
      catchError(error => {
        console.error('[CatalogService] getCategoryViewDetail error', { categoryId, error });
        return throwError(() => error);
      })
    );
  }

  calculateRoomPrice(request: CalculateRoomPriceRequest): Observable<RoomPriceResponse> {
    const url = `${this.catalogUrl}/calculate-room-price`;
    console.info('[CatalogService] POST', url, request);
    return this.http.post<RoomPriceResponse>(url, request).pipe(
      tap(response => console.info('[CatalogService] calculateRoomPrice success', response)),
      catchError(error => {
        console.error('[CatalogService] calculateRoomPrice error', { request, error });
        return throwError(() => error);
      })
    );
  }
}
