import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, Router } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { HomePage } from './home-page';
import { SearchForm } from '../../models/search-form.interface';

describe('HomePage', () => {
  let component: HomePage;
  let fixture: ComponentFixture<HomePage>;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomePage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomePage);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
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

  it('should navigate to /resultados with query params when selectedDestination is set', () => {
    const navigateSpy = spyOn(router, 'navigate');

    const mockForm: SearchForm = {
      location: 'Bordeaux, Nouvelle-Aquitaine, Francia',
      checkIn: '2026-05-01',
      checkOut: '2026-05-07',
      guests: 2,
      selectedDestination: {
        ciudad: 'Bordeaux',
        estado_provincia: 'Nouvelle-Aquitaine',
        pais: 'Francia',
      },
    };

    component.onSearch(mockForm);

    expect(navigateSpy).toHaveBeenCalledWith(['/resultados'], {
      queryParams: {
        ciudad: 'Bordeaux',
        estado_provincia: 'Nouvelle-Aquitaine',
        pais: 'Francia',
        fecha_inicio: '2026-05-01',
        fecha_fin: '2026-05-07',
        huespedes: 2,
      },
    });
  });

  it('should NOT navigate if selectedDestination is undefined', () => {
    const navigateSpy = spyOn(router, 'navigate');

    const mockForm: SearchForm = {
      location: 'Bordeaux',
      checkIn: '2026-05-01',
      checkOut: '2026-05-07',
      guests: 2,
      selectedDestination: undefined,
    };

    component.onSearch(mockForm);

    expect(navigateSpy).not.toHaveBeenCalled();
  });

  it('should default guests to 1 when null', () => {
    const navigateSpy = spyOn(router, 'navigate');

    const mockForm: SearchForm = {
      location: 'Bordeaux, Nouvelle-Aquitaine, Francia',
      checkIn: '2026-05-01',
      checkOut: '2026-05-07',
      guests: null,
      selectedDestination: {
        ciudad: 'Bordeaux',
        estado_provincia: 'Nouvelle-Aquitaine',
        pais: 'Francia',
      },
    };

    component.onSearch(mockForm);

    const callArgs = navigateSpy.calls.mostRecent().args;
    expect(callArgs[1]?.queryParams?.['huespedes']).toBe(1);
  });
});
