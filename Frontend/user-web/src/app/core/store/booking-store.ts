import { Injectable } from '@angular/core';
import { HoldResponse } from '../../models/hold.interface';

export interface BookingSession {
  reservationId: string;
  signature: string;
  expiresAt: number;
}

@Injectable({ providedIn: 'root' })
export class BookingStore {
  private readonly HOLD_KEY_PREFIX = 'hold:';
  private readonly SESSION_KEY_PREFIX = 'booking-session:';

  setHold(reservationId: string | null | undefined, hold: HoldResponse): void {
    const key = this.buildHoldKey(reservationId);
    if (!key) {
      return;
    }

    localStorage.setItem(key, JSON.stringify(hold));
  }

  getHold(reservationId: string | null | undefined): HoldResponse | null {
    const key = this.buildHoldKey(reservationId);
    if (!key) {
      return null;
    }

    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) as HoldResponse : null;
  }

  clear(reservationId: string | null | undefined): void {
    const key = this.buildHoldKey(reservationId);
    if (!key) {
      return;
    }

    localStorage.removeItem(key);
  }

  setBookingSession(signature: string | null | undefined, session: BookingSession): void {
    const key = this.buildSessionKey(signature);
    if (!key) {
      return;
    }

    localStorage.setItem(key, JSON.stringify(session));
  }

  getBookingSession(signature: string | null | undefined): BookingSession | null {
    const key = this.buildSessionKey(signature);
    if (!key) {
      return null;
    }

    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) as BookingSession : null;
  }

  clearBookingSession(signature: string | null | undefined): void {
    const key = this.buildSessionKey(signature);
    if (!key) {
      return;
    }

    localStorage.removeItem(key);
  }

  private buildHoldKey(reservationId: string | null | undefined): string | null {
    const normalizedReservationId = reservationId?.trim();
    if (!normalizedReservationId) {
      return null;
    }

    return `${this.HOLD_KEY_PREFIX}${normalizedReservationId}`;
  }

  private buildSessionKey(signature: string | null | undefined): string | null {
    const normalizedSignature = signature?.trim();
    if (!normalizedSignature) {
      return null;
    }

    return `${this.SESSION_KEY_PREFIX}${normalizedSignature}`;
  }
}