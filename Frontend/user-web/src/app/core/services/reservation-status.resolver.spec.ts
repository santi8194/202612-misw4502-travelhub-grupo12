import { resolveReservationStatus, getStatusLabel } from './reservation-status.resolver';

describe('resolveReservationStatus', () => {
  it('should return CONFIRMADA when booking is CONFIRMADA', () => {
    expect(resolveReservationStatus('CONFIRMADA', 'APPROVED')).toBe('CONFIRMADA');
    expect(resolveReservationStatus('CONFIRMADA', null)).toBe('CONFIRMADA');
  });

  it('should return CANCELADA when booking is CANCELADA', () => {
    expect(resolveReservationStatus('CANCELADA', 'APPROVED')).toBe('CANCELADA');
    expect(resolveReservationStatus('CANCELADA', null)).toBe('CANCELADA');
  });

  it('should return PENDIENTE_PAGO when booking is HOLD and payment is null', () => {
    expect(resolveReservationStatus('HOLD', null)).toBe('PENDIENTE_PAGO');
  });

  it('should return PENDIENTE_PAGO when booking is HOLD and payment is PENDING', () => {
    expect(resolveReservationStatus('HOLD', 'PENDING')).toBe('PENDIENTE_PAGO');
  });

  it('should return PENDIENTE_PAGO when booking is HOLD and payment is REJECTED', () => {
    expect(resolveReservationStatus('HOLD', 'REJECTED')).toBe('PENDIENTE_PAGO');
  });

  it('should return PENDIENTE_CONFIRMACION_HOTEL when booking is HOLD and payment is APPROVED', () => {
    expect(resolveReservationStatus('HOLD', 'APPROVED')).toBe('PENDIENTE_CONFIRMACION_HOTEL');
  });

  it('should return PENDIENTE_PAGO when booking is PENDIENTE and payment is null', () => {
    expect(resolveReservationStatus('PENDIENTE', null)).toBe('PENDIENTE_PAGO');
  });

  it('should return PENDIENTE_CONFIRMACION_HOTEL when booking is PENDIENTE and payment is APPROVED', () => {
    expect(resolveReservationStatus('PENDIENTE', 'APPROVED')).toBe('PENDIENTE_CONFIRMACION_HOTEL');
  });

  it('should return CANCELADA for EXPIRADA booking state', () => {
    expect(resolveReservationStatus('EXPIRADA', null)).toBe('CANCELADA');
  });
});

describe('getStatusLabel', () => {
  it('should return Spanish label for CONFIRMADA', () => {
    expect(getStatusLabel('CONFIRMADA')).toBe('Confirmada');
  });

  it('should return Spanish label for PENDIENTE_PAGO', () => {
    expect(getStatusLabel('PENDIENTE_PAGO')).toBe('Pendiente Pago');
  });

  it('should return Spanish label for PENDIENTE_CONFIRMACION_HOTEL', () => {
    expect(getStatusLabel('PENDIENTE_CONFIRMACION_HOTEL')).toBe('Pendiente Confirmación');
  });

  it('should return Spanish label for CANCELADA', () => {
    expect(getStatusLabel('CANCELADA')).toBe('Cancelada');
  });
});
