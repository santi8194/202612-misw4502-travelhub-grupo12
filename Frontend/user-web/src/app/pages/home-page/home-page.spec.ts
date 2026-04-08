import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { HomePage } from './home-page';

describe('HomePage', () => {
  let component: HomePage;
  let fixture: ComponentFixture<HomePage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomePage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the hero section', () => {
    const hero = fixture.nativeElement.querySelector('[data-testid="hero-section"]');
    expect(hero).toBeTruthy();
  });

  it('should render the hero title with correct text', () => {
    const title = fixture.nativeElement.querySelector('[data-testid="hero-title"]');
    expect(title).toBeTruthy();
    expect(title.textContent.trim()).toBe('¿A dónde quieres ir hoy?');
  });

  it('should render the hero search form', () => {
    const form = fixture.nativeElement.querySelector('[data-testid="hero-search-form"]');
    expect(form).toBeTruthy();
  });

  it('should render the header', () => {
    const header = fixture.nativeElement.querySelector('app-header');
    expect(header).toBeTruthy();
  });

  it('should render the footer', () => {
    const footer = fixture.nativeElement.querySelector('app-footer');
    expect(footer).toBeTruthy();
  });

  it('should log search data when onSearch is called', () => {
    spyOn(console, 'log');
    const mockForm = { location: 'París', checkIn: '2026-05-01', checkOut: '2026-05-07', guests: 2 };

    component.onSearch(mockForm);

    expect(console.log).toHaveBeenCalledWith('[HomePage] Search submitted:', mockForm);
  });
});
