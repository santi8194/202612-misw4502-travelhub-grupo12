import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { MyReservationsPage } from './my-reservations-page';
import { MyReservationsService } from '../../core/services/my-reservations';

describe('MyReservationsPage', () => {
  let fixture: ComponentFixture<MyReservationsPage>;
  let service: MyReservationsService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyReservationsPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MyReservationsPage);
    service = TestBed.inject(MyReservationsService);
    fixture.detectChanges();
  });

  it('should create the component', () => {
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render the header', () => {
    const header = fixture.nativeElement.querySelector('app-header');
    expect(header).toBeTruthy();
  });

  it('should render the footer', () => {
    const footer = fixture.nativeElement.querySelector('app-footer');
    expect(footer).toBeTruthy();
  });

  it('should render the page title', () => {
    const title = fixture.nativeElement.querySelector('[data-testid="page-title"]');
    expect(title).toBeTruthy();
    expect(title.textContent.trim()).toBe('Mis Reservaciones');
  });

  it('should render the page subtitle', () => {
    const subtitle = fixture.nativeElement.querySelector('[data-testid="page-subtitle"]');
    expect(subtitle).toBeTruthy();
    expect(subtitle.textContent.trim()).toBeTruthy();
  });

  it('should render the counter bar', () => {
    const bar = fixture.nativeElement.querySelector('[data-testid="counter-bar"]');
    expect(bar).toBeTruthy();
  });

  it('should render 4 filter buttons in counter bar', () => {
    const todas = fixture.nativeElement.querySelector('[data-testid="filter-todas"]');
    const confirmadas = fixture.nativeElement.querySelector('[data-testid="filter-confirmadas"]');
    const pendientes = fixture.nativeElement.querySelector('[data-testid="filter-pendientes"]');
    const canceladas = fixture.nativeElement.querySelector('[data-testid="filter-canceladas"]');
    expect(todas).toBeTruthy();
    expect(confirmadas).toBeTruthy();
    expect(pendientes).toBeTruthy();
    expect(canceladas).toBeTruthy();
  });

  it('should display correct total count', () => {
    const el = fixture.nativeElement.querySelector('[data-testid="count-total"]');
    expect(el.textContent.trim()).toBe(String(service.counters().total));
  });

  it('should render reservation cards', () => {
    const list = fixture.nativeElement.querySelector('[data-testid="reservations-list"]');
    expect(list).toBeTruthy();
    const cards = list.querySelectorAll('[data-testid="reservation-card"]');
    expect(cards.length).toBeGreaterThan(0);
  });

  it('should show all reservations by default (filter TODAS)', () => {
    expect(service.activeFilter()).toBe('TODAS');
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="reservation-card"]');
    expect(cards.length).toBe(service.reservations().length);
  });

  it('should filter to CONFIRMADA when clicking filter-confirmadas', async () => {
    const btn = fixture.nativeElement.querySelector('[data-testid="filter-confirmadas"]');
    btn.click();
    fixture.detectChanges();
    expect(service.activeFilter()).toBe('CONFIRMADA');
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="reservation-card"]');
    expect(cards.length).toBe(service.filteredReservations().length);
  });

  it('should filter to PENDIENTE when clicking filter-pendientes', async () => {
    const btn = fixture.nativeElement.querySelector('[data-testid="filter-pendientes"]');
    btn.click();
    fixture.detectChanges();
    expect(service.activeFilter()).toBe('PENDIENTE');
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="reservation-card"]');
    expect(cards.length).toBe(service.filteredReservations().length);
  });

  it('should filter to CANCELADA when clicking filter-canceladas', async () => {
    const btn = fixture.nativeElement.querySelector('[data-testid="filter-canceladas"]');
    btn.click();
    fixture.detectChanges();
    expect(service.activeFilter()).toBe('CANCELADA');
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="reservation-card"]');
    expect(cards.length).toBe(service.filteredReservations().length);
  });

  it('should show empty state when no reservations match the filter', async () => {
    // Force an empty filtered result by setting all to CONFIRMADA and filtering CANCELADA
    service.reservations.set([]);
    service.setFilter('CANCELADA');
    fixture.detectChanges();
    const emptyState = fixture.nativeElement.querySelector('[data-testid="empty-state"]');
    expect(emptyState).toBeTruthy();
  });

  it('should return to all reservations when clicking filter-todas', async () => {
    // First filter then reset
    const btnConfirmadas = fixture.nativeElement.querySelector('[data-testid="filter-confirmadas"]');
    btnConfirmadas.click();
    fixture.detectChanges();

    const btnTodas = fixture.nativeElement.querySelector('[data-testid="filter-todas"]');
    btnTodas.click();
    fixture.detectChanges();

    expect(service.activeFilter()).toBe('TODAS');
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="reservation-card"]');
    expect(cards.length).toBe(service.reservations().length);
  });
});
