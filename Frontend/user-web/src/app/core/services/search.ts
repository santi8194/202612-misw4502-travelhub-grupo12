import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { DestinationResponse } from '../../models/destination.interface';
import { SearchResultsResponse } from '../../models/hospedaje.interface';
import { SearchRequest } from '../../models/search-request.interface';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private readonly http = inject(HttpClient);
  private readonly destinationsUrl = `${environment.apiBaseUrl}/v1/search/destinations`;
  private readonly searchUrl = `${environment.apiBaseUrl}/v1/search`;

  autocompleteDestinations(query: string): Observable<DestinationResponse> {
    const params = new HttpParams().set('q', query);
    return this.http.get<DestinationResponse>(this.destinationsUrl, { params });
  }

  searchHospedajes(request: SearchRequest): Observable<SearchResultsResponse> {
    const params = new HttpParams()
      .set('ciudad', request.ciudad)
      .set('estado_provincia', request.estado_provincia)
      .set('pais', request.pais)
      .set('fecha_inicio', request.fecha_inicio)
      .set('fecha_fin', request.fecha_fin)
      .set('huespedes', request.huespedes.toString());
    return this.http.get<SearchResultsResponse>(this.searchUrl, { params });
  }
}
