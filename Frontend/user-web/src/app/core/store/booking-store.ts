import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({ providedIn: 'root' })
export class BookingStore {

  constructor(@Inject(PLATFORM_ID) private platformId: object) {}

  private get storage(): Storage | null {
    return isPlatformBrowser(this.platformId) ? localStorage : null;
  }

  setHold(hold: any) {
    this.storage?.setItem('hold', JSON.stringify(hold));
  }

  getHold() {
    return JSON.parse(this.storage?.getItem('hold') || 'null');
  }

  clear() {
    this.storage?.removeItem('hold');
  }
}