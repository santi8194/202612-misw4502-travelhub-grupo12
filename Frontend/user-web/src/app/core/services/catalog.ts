import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { RoomDetailResponse } from '../../models/room-detail.interface';

@Injectable({ providedIn: 'root' })
export class CatalogService {
  private readonly http = inject(HttpClient);
  private readonly catalogUrl = environment.catalogApiUrl;

  getCategoryViewDetail(categoryId: string): Observable<RoomDetailResponse> {
    const url = `${this.catalogUrl}/categories/${categoryId}/view-detail`;
    console.info('[CatalogService] GET', url);
    return this.http.get<RoomDetailResponse>(url).pipe(
      tap(response => console.info('[CatalogService] getCategoryViewDetail success', response)),
      catchError(error => {
        console.error('[CatalogService] getCategoryViewDetail error', { categoryId, error });
        return throwError(() => error);
      })
    );
  }
}
