import { TestBed } from '@angular/core/testing';

import { BookingStore } from './booking-store';

describe('BookingStore', () => {
  let service: BookingStore;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BookingStore);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
