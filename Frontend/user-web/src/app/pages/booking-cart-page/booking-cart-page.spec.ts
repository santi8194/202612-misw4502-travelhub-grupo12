import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { BookingCartPage } from './booking-cart-page';

describe('BookingCartPage', () => {
  let component: BookingCartPage;
  let fixture: ComponentFixture<BookingCartPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BookingCartPage],
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(BookingCartPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize form with empty values', () => {
    const form = component.form();
    expect(form.name).toBe('');
    expect(form.lastName).toBe('');
    expect(form.email).toBe('');
    expect(form.phone).toBe('');
    expect(form.detailedRequest).toBe('');
  });

  it('should have timer inactive initially', () => {
    expect(component.timerActive()).toBeFalse();
    expect(component.remainingTime()).toBe(0);
  });

  it('should render the continue button', () => {
    const btn = fixture.nativeElement.querySelector('[data-testid="continue-payment-btn"]');
    expect(btn).toBeTruthy();
    expect(btn.textContent.trim()).toContain('Continuar con el pago');
  });

  it('should render the inline error message when hold creation fails', () => {
    component.holdError.set('La categoria seleccionada no existe o ya no está disponible.');

    fixture.detectChanges();

    const error = fixture.nativeElement.querySelector('[data-testid="booking-cart-error"]');
    expect(error).toBeTruthy();
    expect(error.textContent).toContain('La categoria seleccionada no existe o ya no está disponible.');
  });

  it('should hide hold timer when redirecting to an existing session', () => {
    component.isRedirectingToExistingSession.set(true);
    component.remainingTime.set(120);

    fixture.detectChanges();

    const timer = fixture.nativeElement.querySelector('[data-testid="hold-timer"]');
    expect(timer).toBeNull();
  });
});
