import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { GuestsPage } from './guests-page';

describe('GuestsPage', () => {
  let component: GuestsPage;
  let fixture: ComponentFixture<GuestsPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GuestsPage],
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(GuestsPage);
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
});
