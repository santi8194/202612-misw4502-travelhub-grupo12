import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { HeroSearchFormComponent } from './hero-search-form';

describe('HeroSearchFormComponent', () => {
  let component: HeroSearchFormComponent;
  let fixture: ComponentFixture<HeroSearchFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeroSearchFormComponent],
      providers: [provideZonelessChangeDetection()],
    }).compileComponents();

    fixture = TestBed.createComponent(HeroSearchFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the search form', () => {
    const form = fixture.nativeElement.querySelector('[data-testid="hero-search-form"]');
    expect(form).toBeTruthy();
  });

  it('should render the location input', () => {
    const input = fixture.nativeElement.querySelector('[data-testid="input-location"]');
    expect(input).toBeTruthy();
  });

  it('should render the check-in input', () => {
    const input = fixture.nativeElement.querySelector('[data-testid="input-checkin"]');
    expect(input).toBeTruthy();
  });

  it('should render the check-out input', () => {
    const input = fixture.nativeElement.querySelector('[data-testid="input-checkout"]');
    expect(input).toBeTruthy();
  });

  it('should render the guests input', () => {
    const input = fixture.nativeElement.querySelector('[data-testid="input-guests"]');
    expect(input).toBeTruthy();
  });

  it('should render the search button', () => {
    const btn = fixture.nativeElement.querySelector('[data-testid="btn-search"]');
    expect(btn).toBeTruthy();
  });

  it('should initialize form with empty values', () => {
    const form = component.form();
    expect(form.location).toBe('');
    expect(form.checkIn).toBe('');
    expect(form.checkOut).toBe('');
    expect(form.guests).toBeNull();
  });

  it('should update location field', () => {
    component.updateField('location', 'París');
    expect(component.form().location).toBe('París');
  });

  it('should emit search event on form submit', () => {
    let emitted = false;
    component.search.subscribe(() => (emitted = true));

    component.updateField('location', 'Roma');
    component.onSearch();

    expect(emitted).toBeTrue();
  });

  it('should emit current form data on search', () => {
    let emittedForm = null as unknown;
    component.search.subscribe(val => (emittedForm = val));

    component.updateField('location', 'Bogotá');
    component.updateField('guests', 3);
    component.onSearch();

    expect((emittedForm as { location: string }).location).toBe('Bogotá');
    expect((emittedForm as { guests: number }).guests).toBe(3);
  });
});
