import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { BookingSession, BookingStore } from './booking-store';
import { HoldResponse } from '../../models/hold.interface';

describe('BookingStore', () => {
  let store: BookingStore;
  const reservationA = 'reserva-1';
  const reservationB = 'reserva-2';

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideZonelessChangeDetection()],
    });
    store = TestBed.inject(BookingStore);
    localStorage.clear();
  });

  afterEach(() => localStorage.clear());

  it('should be created', () => {
    expect(store).toBeTruthy();
  });

  it('should store and retrieve a hold', () => {
    const hold: HoldResponse = { id: 'hold-1', expiresAt: Date.now() + 60000 };
    store.setHold(reservationA, hold);

    const retrieved = store.getHold(reservationA);
    expect(retrieved).toEqual(hold);
  });

  it('should return null when no hold exists', () => {
    expect(store.getHold(reservationA)).toBeNull();
  });

  it('should clear stored hold', () => {
    const hold: HoldResponse = { id: 'hold-2', expiresAt: Date.now() + 60000 };
    store.setHold(reservationA, hold);
    store.clear(reservationA);

    expect(store.getHold(reservationA)).toBeNull();
  });

  it('should keep holds isolated by reservation id', () => {
    const holdA: HoldResponse = { id: 'hold-a', expiresAt: Date.now() + 60000 };
    const holdB: HoldResponse = { id: 'hold-b', expiresAt: Date.now() + 120000 };

    store.setHold(reservationA, holdA);
    store.setHold(reservationB, holdB);

    expect(store.getHold(reservationA)).toEqual(holdA);
    expect(store.getHold(reservationB)).toEqual(holdB);
  });

  it('should ignore empty reservation ids', () => {
    const hold: HoldResponse = { id: 'hold-empty', expiresAt: Date.now() + 60000 };

    store.setHold('', hold);

    expect(store.getHold('')).toBeNull();
  });

  it('should ignore null, undefined and blank reservation ids', () => {
    const hold: HoldResponse = { id: 'hold-blank', expiresAt: Date.now() + 60000 };

    store.setHold(null, hold);
    store.setHold(undefined, hold);
    store.setHold('   ', hold);
    store.clear(null);
    store.clear(undefined);
    store.clear('   ');

    expect(store.getHold(null)).toBeNull();
    expect(store.getHold(undefined)).toBeNull();
    expect(store.getHold('   ')).toBeNull();
    expect(localStorage.length).toBe(0);
  });

  it('should store and retrieve a booking session by signature', () => {
    const session: BookingSession = {
      reservationId: reservationA,
      signature: 'categoria-1|2026-04-12|2026-04-14|2',
      expiresAt: Date.now() + 60000,
    };

    store.setBookingSession(session.signature, session);

    expect(store.getBookingSession(session.signature)).toEqual(session);
  });

  it('should clear a stored booking session', () => {
    const session: BookingSession = {
      reservationId: reservationA,
      signature: 'categoria-1|2026-04-12|2026-04-14|2',
      expiresAt: Date.now() + 60000,
    };

    store.setBookingSession(session.signature, session);
    store.clearBookingSession(session.signature);

    expect(store.getBookingSession(session.signature)).toBeNull();
  });

  it('should ignore blank booking session signatures', () => {
    const session: BookingSession = {
      reservationId: reservationA,
      signature: '   ',
      expiresAt: Date.now() + 60000,
    };

    store.setBookingSession(null, session);
    store.setBookingSession(undefined, session);
    store.setBookingSession('   ', session);
    store.clearBookingSession(null);
    store.clearBookingSession(undefined);
    store.clearBookingSession('   ');

    expect(store.getBookingSession(null)).toBeNull();
    expect(store.getBookingSession(undefined)).toBeNull();
    expect(store.getBookingSession('   ')).toBeNull();
    expect(localStorage.length).toBe(0);
  });
});
