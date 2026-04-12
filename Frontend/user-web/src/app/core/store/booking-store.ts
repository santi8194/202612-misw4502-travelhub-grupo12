import { Injectable } from '@angular/core';
import { HoldResponse } from '../../models/hold.interface';

@Injectable({ providedIn: 'root' })
export class BookingStore {
  private readonly HOLD_KEY = 'hold';

  setHold(hold: HoldResponse): void {
    localStorage.setItem(this.HOLD_KEY, JSON.stringify(hold));
  }

  getHold(): HoldResponse | null {
    const raw = localStorage.getItem(this.HOLD_KEY);
    return raw ? JSON.parse(raw) as HoldResponse : null;
  }

  clear(): void {
    localStorage.removeItem(this.HOLD_KEY);
  }
}