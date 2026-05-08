import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection, signal } from '@angular/core';
import { provideRouter } from '@angular/router';
import { ReservationCardComponent } from './reservation-card';
import { ReservationViewModel } from '../../../models/reservation.interface';

function makeReservation(overrides: Partial<ReservationViewModel> = {}): ReservationViewModel {
  return {
    id_reserva: 'test-uuid-1234',
    nombre_comercial: 'Test Hotel',
    foto_portada_url: null,
    estado: 'CONFIRMADA',
    fecha_check_in: '2026-05-01',
    fecha_check_out: '2026-05-05',
    total_huespedes: 2,
    monto_total: 500,
    moneda: 'USD',
    codigo_confirmacion: 'TH-001',
    ...overrides,
  };
}

describe('ReservationCardComponent', () => {
  let fixture: ComponentFixture<ReservationCardComponent>;

  async function setup(reservation: ReservationViewModel) {
    await TestBed.configureTestingModule({
      imports: [ReservationCardComponent],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ReservationCardComponent);
    fixture.componentRef.setInput('reservation', reservation);
    fixture.detectChanges();
  }

  it('should create the component', async () => {
    await setup(makeReservation());
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should display nombre_comercial in reservation-name', async () => {
    await setup(makeReservation({ nombre_comercial: 'Coastal Paradise' }));
    const el = fixture.nativeElement.querySelector('[data-testid="reservation-name"]');
    expect(el.textContent.trim()).toBe('Coastal Paradise');
  });

  it('should display status badge for CONFIRMADA', async () => {
    await setup(makeReservation({ estado: 'CONFIRMADA' }));
    const badge = fixture.nativeElement.querySelector('[data-testid="reservation-status-badge"]');
    expect(badge.textContent.trim()).toBe('Confirmada');
    expect(badge.classList).toContain('badge--confirmada');
  });

  it('should display status badge for PENDIENTE_PAGO', async () => {
    await setup(makeReservation({ estado: 'PENDIENTE_PAGO' }));
    const badge = fixture.nativeElement.querySelector('[data-testid="reservation-status-badge"]');
    expect(badge.textContent.trim()).toBe('Pendiente Pago');
    expect(badge.classList).toContain('badge--pendiente-pago');
  });

  it('should display status badge for PENDIENTE_CONFIRMACION_HOTEL', async () => {
    await setup(makeReservation({ estado: 'PENDIENTE_CONFIRMACION_HOTEL' }));
    const badge = fixture.nativeElement.querySelector('[data-testid="reservation-status-badge"]');
    expect(badge.textContent.trim()).toBe('Pendiente Confirmación');
    expect(badge.classList).toContain('badge--pendiente-hotel');
  });

  it('should display status badge for CANCELADA', async () => {
    await setup(makeReservation({ estado: 'CANCELADA' }));
    const badge = fixture.nativeElement.querySelector('[data-testid="reservation-status-badge"]');
    expect(badge.textContent.trim()).toBe('Cancelada');
    expect(badge.classList).toContain('badge--cancelada');
  });

  it('should display check-in date', async () => {
    await setup(makeReservation({ fecha_check_in: '2026-05-01' }));
    const el = fixture.nativeElement.querySelector('[data-testid="check-in-date"]');
    expect(el).toBeTruthy();
    expect(el.textContent.trim()).toBeTruthy();
  });

  it('should display check-out date', async () => {
    await setup(makeReservation({ fecha_check_out: '2026-05-05' }));
    const el = fixture.nativeElement.querySelector('[data-testid="check-out-date"]');
    expect(el).toBeTruthy();
    expect(el.textContent.trim()).toBeTruthy();
  });

  it('should display total guests', async () => {
    await setup(makeReservation({ total_huespedes: 3 }));
    const el = fixture.nativeElement.querySelector('[data-testid="total-guests"]');
    expect(el.textContent.trim()).toBe('3');
  });

  it('should display formatted price when monto_total is set', async () => {
    await setup(makeReservation({ monto_total: 1500, moneda: 'USD' }));
    const el = fixture.nativeElement.querySelector('[data-testid="reservation-price"]');
    expect(el.textContent).toContain('1,500');
  });

  it('should always render Ver detalles button', async () => {
    await setup(makeReservation({ estado: 'CONFIRMADA' }));
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-ver-detalles"]');
    expect(btn).toBeTruthy();
    expect(btn.textContent.trim()).toContain('Ver detalles');
  });

  it('should show Completar Pago button for PENDIENTE_PAGO', async () => {
    await setup(makeReservation({ estado: 'PENDIENTE_PAGO' }));
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-completar-pago"]');
    expect(btn).toBeTruthy();
  });

  it('should NOT show Completar Pago for CONFIRMADA', async () => {
    await setup(makeReservation({ estado: 'CONFIRMADA' }));
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-completar-pago"]');
    expect(btn).toBeNull();
  });

  it('should show Cancelar Reserva for CONFIRMADA', async () => {
    await setup(makeReservation({ estado: 'CONFIRMADA' }));
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-cancelar-reserva"]');
    expect(btn).toBeTruthy();
  });

  it('should show Cancelar Reserva for PENDIENTE_CONFIRMACION_HOTEL', async () => {
    await setup(makeReservation({ estado: 'PENDIENTE_CONFIRMACION_HOTEL' }));
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-cancelar-reserva"]');
    expect(btn).toBeTruthy();
  });

  it('should NOT show Cancelar Reserva for CANCELADA', async () => {
    await setup(makeReservation({ estado: 'CANCELADA' }));
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-cancelar-reserva"]');
    expect(btn).toBeNull();
  });

  it('should NOT show Cancelar Reserva for PENDIENTE_PAGO', async () => {
    await setup(makeReservation({ estado: 'PENDIENTE_PAGO' }));
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-cancelar-reserva"]');
    expect(btn).toBeNull();
  });

  it('should show image when foto_portada_url is set', async () => {
    await setup(makeReservation({ foto_portada_url: 'https://example.com/img.jpg' }));
    const img = fixture.nativeElement.querySelector('[data-testid="card-image"] img');
    expect(img).toBeTruthy();
    expect(img.src).toContain('example.com');
  });

  it('should show placeholder when foto_portada_url is null', async () => {
    await setup(makeReservation({ foto_portada_url: null }));
    const placeholder = fixture.nativeElement.querySelector('.card-image__placeholder');
    expect(placeholder).toBeTruthy();
    const img = fixture.nativeElement.querySelector('[data-testid="card-image"] img');
    expect(img).toBeNull();
  });
});
