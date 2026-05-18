import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ReservationStatusEmailPayload {
  id_reserva: string;
  email_cliente: string;
  estado: 'CONFIRMADA' | 'CANCELADA';
  codigo_reserva?: string;
  monto_reembolso?: number;
  moneda_reembolso?: string;
  detalle_reembolso?: string;
}

@Injectable({ providedIn: 'root' })
export class ReservationEmailNotificationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.notificationApiUrl;

  sendReservationStatusEmail(payload: ReservationStatusEmailPayload): Observable<unknown> {
    return this.http.post(`${this.apiUrl}/notifications/reservations/status-email`, payload);
  }
}
