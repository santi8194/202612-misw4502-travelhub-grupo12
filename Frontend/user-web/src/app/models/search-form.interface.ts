import { DestinationItem } from './destination.interface';

export interface SearchForm {
  location: string;
  checkIn: string;
  checkOut: string;
  guests: number | null;
  selectedDestination?: DestinationItem;
}
