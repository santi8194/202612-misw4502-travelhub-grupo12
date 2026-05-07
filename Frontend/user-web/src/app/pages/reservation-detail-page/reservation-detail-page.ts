import type { ReservationStatus } from '../../models/reservation.interface';

interface ReservationDetail {
  id: string;
  hotelName: string;
  location: {
    city: string;
    country: string;
  };
  checkInDate: string;
  checkOutDate: string;
  guests: number;
  confirmationNumber: string | null;
  status: ReservationStatus;
  totalAmount: number | null;
  currency: string;
  images: string[];
  canCancel: boolean;
  cancellationReason?: string;
}
