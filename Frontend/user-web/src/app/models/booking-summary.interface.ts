export interface BookingSummaryData {
  propertyName: string;
  location: string;
  imageUrl: string;
  checkIn: string;
  checkOut: string;
  guests: number;
  nights: number;
  pricePerNight: number;
  subtotal: number;
  taxesAndFees: number;
  total: number;
  currency: string;
  currencySymbol: string;
  taxesAndFeesLabel: string;
}
