import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { DestinationResponse } from '../../models/destination.interface';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiBaseUrl}/v1/search/destinations`;

  autocompleteDestinations(query: string): Observable<DestinationResponse> {
    const params = new HttpParams().set('q', query);
    return this.http.get<DestinationResponse>(this.apiUrl, { params });
  }
}
