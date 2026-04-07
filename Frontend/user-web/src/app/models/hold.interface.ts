export interface HoldRequest {
  categoryId: number;
  checkIn: string;
  checkOut: string;
  guests: number;
}

export interface HoldResponse {
  id: string;
  expiresAt: number;
}
