import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class BookingService {

  async createHold(data: any): Promise<any> {

    // 🔥 MOCK (luego cambias a HTTP)
    return new Promise((resolve, reject) => {

      const hasAvailability = true;

      if (!hasAvailability) {
        reject('No availability');
      }

      resolve({
        id: 'hold-123',
        expiresAt: Date.now() + 15 * 60 * 1000
      });
    });
  }
}