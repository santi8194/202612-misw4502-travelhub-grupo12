import { TestBed } from '@angular/core/testing';
import { BookingStore } from './booking-store';
import { HoldResponse } from '../../models/hold.interface';

describe('BookingStore', () => {
  let store: BookingStore;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    store = TestBed.inject(BookingStore);
    localStorage.clear();
  });

  afterEach(() => localStorage.clear());

  it('should be created', () => {
    expect(store).toBeTruthy();
  });

  it('should store and retrieve a hold', () => {
    const hold: HoldResponse = { id: 'hold-1', expiresAt: Date.now() + 60000 };
    store.setHold(hold);

    const retrieved = store.getHold();
    expect(retrieved).toEqual(hold);
  });

  it('should return null when no hold exists', () => {
    expect(store.getHold()).toBeNull();
  });

  it('should clear stored hold', () => {
    const hold: HoldResponse = { id: 'hold-2', expiresAt: Date.now() + 60000 };
    store.setHold(hold);
    store.clear();

    expect(store.getHold()).toBeNull();
  });
});
