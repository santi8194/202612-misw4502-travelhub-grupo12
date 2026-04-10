import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { SearchResultsPage } from './search-results-page';
import { Hospedaje } from '../../models/hospedaje.interface';

const mockHospedaje: Hospedaje = {
  id_propiedad: '550e8400-e29b-41d4-a716-446655440000',
  id_categoria: '550e8400-e29b-41d4-a716-446655440010',
  propiedad_nombre: 'Hotel',
  categoria_nombre: 'Bordeaux Getaway',
  imagen_principal_url: 'https://example.com/img.jpg',
  amenidades_destacadas: ['Wifi', 'Cocina', 'Cuarto de ropa', 'Piscina'],
  estrellas: 5,
  rating_promedio: 5.0,
  ciudad: 'Bordeaux',
  estado_provincia: 'Nouvelle-Aquitaine',
  pais: 'Francia',
  coordenadas: { lat: 44.8378, lon: -0.5792 },
  capacidad_pax: 2,
  precio_base: '75.00',
  moneda: 'USD',
  es_reembolsable: true,
};

describe('SearchResultsPage', () => {
  let component: SearchResultsPage;
  let fixture: ComponentFixture<SearchResultsPage>;
  let httpTesting: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchResultsPage],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([
          { path: 'resultados', component: SearchResultsPage },
        ]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SearchResultsPage);
    component = fixture.componentInstance;
    httpTesting = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => httpTesting.verify());

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the main content area', () => {
    const main = fixture.nativeElement.querySelector('[data-testid="results-main"]');
    expect(main).toBeTruthy();
  });

  it('should render the results header section', () => {
    const header = fixture.nativeElement.querySelector('[data-testid="results-header"]');
    expect(header).toBeTruthy();
  });

  it('should render the divider', () => {
    const divider = fixture.nativeElement.querySelector('[data-testid="results-divider"]');
    expect(divider).toBeTruthy();
  });

  it('should render the header component', () => {
    const header = fixture.nativeElement.querySelector('app-header');
    expect(header).toBeTruthy();
  });

  it('should render the footer component', () => {
    const footer = fixture.nativeElement.querySelector('app-footer');
    expect(footer).toBeTruthy();
  });

  it('should show empty state when there are no results and loading is false', () => {
    component.loading.set(false);
    fixture.detectChanges();

    const empty = fixture.nativeElement.querySelector('[data-testid="results-empty"]');
    expect(empty).toBeTruthy();
  });

  it('should show empty state message', () => {
    component.loading.set(false);
    fixture.detectChanges();

    const message = fixture.nativeElement.querySelector('[data-testid="results-empty-message"]');
    expect(message).toBeTruthy();
    expect(message.textContent).toContain('No se encontraron hospedajes');
  });

  it('should show link to homepage in empty state', () => {
    component.loading.set(false);
    fixture.detectChanges();

    const link = fixture.nativeElement.querySelector('[data-testid="results-empty-link"]');
    expect(link).toBeTruthy();
    expect(link.textContent.trim()).toContain('Volver a TravelHub');
  });

  it('should start with 0 hospedajes', () => {
    expect(component.hospedajes()?.length ?? 0).toBe(0);
  });

  it('should have totalResultados computed as 0 initially', () => {
    expect(component.totalResultados()).toBe(0);
  });
});
