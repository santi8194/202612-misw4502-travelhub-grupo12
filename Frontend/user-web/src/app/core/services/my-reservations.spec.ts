import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { MyReservationsService } from './my-reservations';

describe('MyReservationsService', () => {
  let service: MyReservationsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideZonelessChangeDetection()],
    });
    service = TestBed.inject(MyReservationsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return mock reservations with length > 0', () => {
    expect(service.reservations().length).toBeGreaterThan(0);
  });

  it('should compute total counter equal to reservations length', () => {
    expect(service.counters().total).toBe(service.reservations().length);
  });

  it('should count confirmadas correctly', () => {
    const expected = service.reservations().filter(r => r.estado === 'CONFIRMADA').length;
    expect(service.counters().confirmadas).toBe(expected);
  });

  it('should count pendientes as sum of PENDIENTE_PAGO and PENDIENTE_CONFIRMACION_HOTEL', () => {
    const expected = service.reservations().filter(
      r => r.estado === 'PENDIENTE_PAGO' || r.estado === 'PENDIENTE_CONFIRMACION_HOTEL'
    ).length;
    expect(service.counters().pendientes).toBe(expected);
  });

  it('should count canceladas correctly', () => {
    const expected = service.reservations().filter(r => r.estado === 'CANCELADA').length;
    expect(service.counters().canceladas).toBe(expected);
  });

  it('should return all reservations when filter is TODAS', () => {
    service.setFilter('TODAS');
    expect(service.filteredReservations().length).toBe(service.reservations().length);
  });

  it('should filter only CONFIRMADA reservations', () => {
    service.setFilter('CONFIRMADA');
    const filtered = service.filteredReservations();
    expect(filtered.every(r => r.estado === 'CONFIRMADA')).toBeTrue();
  });

  it('should filter PENDIENTE to include both PENDIENTE_PAGO and PENDIENTE_CONFIRMACION_HOTEL', () => {
    service.setFilter('PENDIENTE');
    const filtered = service.filteredReservations();
    filtered.forEach(r => {
      expect(['PENDIENTE_PAGO', 'PENDIENTE_CONFIRMACION_HOTEL']).toContain(r.estado);
    });
  });

  it('should filter only CANCELADA reservations', () => {
    service.setFilter('CANCELADA');
    const filtered = service.filteredReservations();
    expect(filtered.every(r => r.estado === 'CANCELADA')).toBeTrue();
  });

  it('should update activeFilter signal on setFilter', () => {
    service.setFilter('CONFIRMADA');
    expect(service.activeFilter()).toBe('CONFIRMADA');

    service.setFilter('TODAS');
    expect(service.activeFilter()).toBe('TODAS');
  });
});
