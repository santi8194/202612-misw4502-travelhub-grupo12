import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, map, tap, throwError } from 'rxjs';
import { HoldRequest, HoldResponse } from '../../models/hold.interface';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth';

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
  id_reserva?: string;
  mensaje?: string;
  detail?: string;
  error?: string;
}

interface FormalizeBookingResponse {
  mensaje?: string;
  detail?: string;
  error?: string;
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly apiUrl = environment.bookingApiUrl;
  private readonly catalogUrl = environment.catalogApiUrl;

  getReservationErrorMessage(
    error: unknown,
    fallback = 'No fue posible crear la reserva. Intenta nuevamente.'
  ): string {
    const status = error instanceof HttpErrorResponse ? error.status : undefined;
    const backendMessage = this.extractErrorMessage(error);
    const normalizedMessage = this.normalizeErrorMessage(backendMessage);

    if (status === 0) {
      return 'No fue posible comunicarse con el servicio de reservas. Intenta nuevamente en unos minutos.';
    }

    if (backendMessage && !this.isGenericBackendMessage(normalizedMessage)) {
      return backendMessage;
    }

    if (this.isMissingCategoryError(normalizedMessage) || (status === 404 && !normalizedMessage)) {
      return 'La categoria seleccionada no existe o ya no está disponible. Regresa y elige otra opción.';
    }

    if (this.isAvailabilityError(normalizedMessage) || status === 409) {
      return 'Ya no hay disponibilidad para las fechas seleccionadas. Elige otra categoria o cambia las fechas.';
    }

    if (status === 422 || this.isValidationError(normalizedMessage)) {
      return 'La reserva no se pudo crear porque los datos enviados no son válidos. Verifica las fechas y la cantidad de huespedes.';
    }

    if (status === 400) {
      return 'No hay disponibilidad para la categoria en la fecha seleccionada. Elige otra fecha o una categoria diferente.';
    }

    if (status && status >= 500) {
      return 'El servicio de reservas presentó un error. Intenta nuevamente.';
    }

    return fallback;
  }

  createHold(request: HoldRequest): Observable<HoldResponse> {
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      return throwError(() => new Error('Tu sesión no está activa. Inicia sesión para continuar con la reserva.'));
    }

    const mappedRequest: CreateBookingRequest = {
      id_usuario: userId,
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
        const validatedResponse = this.requireBookingId(response);

        // Backend create endpoint does not provide an expiration timestamp.
        return {
          id: validatedResponse.id_reserva,
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

  expireBookingById(idReserva: string): Observable<any> {
    const url = `${this.apiUrl}/${idReserva}/expirar`;
    console.info('[BookingService] POST', url);
    return this.http.post<any>(url, {}).pipe(
      tap((response) => console.info('[BookingService] expireBookingById success', response)),
      catchError((error) => {
        console.error('[BookingService] expireBookingById error', { idReserva, error });
        return throwError(() => error);
      })
    );
  }

  formalizeBookingById(idReserva: string): Observable<FormalizeBookingResponse> {
    const url = `${this.apiUrl}/${idReserva}/formalizar`;
    console.info('[BookingService] POST', url);
    return this.http.post<FormalizeBookingResponse>(url, {}).pipe(
      tap((response) => console.info('[BookingService] formalizeBookingById success', response)),
      catchError((error) => {
        console.error('[BookingService] formalizeBookingById error', { idReserva, error });
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

  getCategoryById(idCategoria: string): Observable<any> {
    const url = `${this.catalogUrl}/categories/${idCategoria}`;
    console.info('[BookingService] GET', url);
    return this.http.get<any>(url).pipe(
      tap((response) => console.info('[BookingService] getCategoryById success', response)),
      catchError((error) => {
        console.error('[BookingService] getCategoryById error', { idCategoria, error });
        return throwError(() => error);
      })
    );
  }

  getPropertyById(propertyId: string): Observable<any> {
    const primaryUrl = `${this.catalogUrl}/properties/${propertyId}`;
    const fallbackUrl = `${this.catalogUrl}/property/${propertyId}`;

    console.info('[BookingService] GET', primaryUrl);
    return this.http.get<any>(primaryUrl).pipe(
      tap((response) => console.info('[BookingService] getPropertyById success', response)),
      catchError((primaryError) => {
        console.warn('[BookingService] getPropertyById primary path failed, trying fallback', {
          propertyId,
          primaryUrl,
          primaryError,
        });

        console.info('[BookingService] GET', fallbackUrl);
        return this.http.get<any>(fallbackUrl).pipe(
          tap((response) => console.info('[BookingService] getPropertyById fallback success', response)),
          catchError((fallbackError) => {
            console.error('[BookingService] getPropertyById error on both paths', {
              propertyId,
              primaryUrl,
              fallbackUrl,
              primaryError,
              fallbackError,
            });
            return throwError(() => fallbackError);
          })
        );
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
      map((response) => this.requireBookingId(response)),
      catchError((error) => {
        console.error('[BookingService] createBooking error', { request, error });
        return throwError(() => error);
      })
    );
  }

  private requireBookingId(response: CreateBookingResponse | null | undefined): CreateBookingResponse & { id_reserva: string } {
    if (response?.id_reserva) {
      return response as CreateBookingResponse & { id_reserva: string };
    }

    const backendMessage = this.extractMessageFromPayload(response);
    if (backendMessage) {
      throw new Error(backendMessage);
    }

    throw new Error('El servicio de reservas no devolvió un identificador de reserva válido.');
  }

  private extractErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      return this.extractMessageFromPayload(error.error)
        ?? this.extractMessageFromPayload(error.message)
        ?? '';
    }

    if (error instanceof Error) {
      return error.message.trim();
    }

    if (typeof error === 'string') {
      return error.trim();
    }

    return this.extractMessageFromPayload(error) ?? '';
  }

  private extractMessageFromPayload(payload: unknown): string | null {
    if (typeof payload === 'string') {
      const trimmed = payload.trim();
      return trimmed.length > 0 ? trimmed : null;
    }

    if (Array.isArray(payload)) {
      for (const item of payload) {
        const message = this.extractMessageFromPayload(item);
        if (message) {
          return message;
        }
      }

      return null;
    }

    if (!payload || typeof payload !== 'object') {
      return null;
    }

    const record = payload as Record<string, unknown>;
    const knownKeys = ['mensaje', 'message', 'detail', 'error', 'descripcion', 'title'];

    for (const key of knownKeys) {
      const message = this.extractMessageFromPayload(record[key]);
      if (message) {
        return message;
      }
    }

    return this.extractMessageFromPayload(record['errors']);
  }

  private normalizeErrorMessage(message: string): string {
    return message
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();
  }

  private isMissingCategoryError(message: string): boolean {
    const mentionsCategory = /categoria|category/.test(message);
    const mentionsMissing = /no existe|does not exist|not found|no encontrada|no encontrado|invalida|invalid/.test(message);
    return mentionsCategory && mentionsMissing;
  }

  private isAvailabilityError(message: string): boolean {
    return /disponib|cupos?|agotad|sold out|sin habitaciones|overbook|capacity|ocupad|inventario/.test(message);
  }

  private isValidationError(message: string): boolean {
    return /fechas?|check.?in|check.?out|huesped|guest|ocupacion|datos? invalid|validation/.test(message);
  }

  private isGenericBackendMessage(message: string): boolean {
    return /bad request|http failure response|internal server error|unexpected error|error$|request failed|status \d+/.test(message);
  }
}