import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { SearchService } from './search';
import { SearchRequest } from '../../models/search-request.interface';

const mockRequest: SearchRequest = {
  ciudad: 'Bordeaux',
  estado_provincia: 'Nouvelle-Aquitaine',
  pais: 'Francia',
  fecha_inicio: '2026-05-01',
  fecha_fin: '2026-05-07',
  huespedes: 2,
};

describe('SearchService', () => {
  let service: SearchService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(SearchService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('autocompleteDestinations', () => {
    it('should send GET to /destinations with query param q', () => {
      service.autocompleteDestinations('Bor').subscribe();

      const req = httpTesting.expectOne(r => r.url.endsWith('/v1/search/destinations'));
      expect(req.request.method).toBe('GET');
      expect(req.request.params.get('q')).toBe('Bor');
      req.flush({ results: [] });
    });
  });

  describe('searchHospedajes', () => {
    it('should send GET to /search with all 6 required params', () => {
      service.searchHospedajes(mockRequest).subscribe();

      const req = httpTesting.expectOne(r => r.url.endsWith('/v1/search'));
      expect(req.request.method).toBe('GET');
      expect(req.request.params.get('ciudad')).toBe('Bordeaux');
      expect(req.request.params.get('estado_provincia')).toBe('Nouvelle-Aquitaine');
      expect(req.request.params.get('pais')).toBe('Francia');
      expect(req.request.params.get('fecha_inicio')).toBe('2026-05-01');
      expect(req.request.params.get('fecha_fin')).toBe('2026-05-07');
      expect(req.request.params.get('huespedes')).toBe('2');
      req.flush({ resultados: [], total: 0 });
    });

    it('should return SearchResultsResponse', () => {
      const mockResponse = {
        resultados: [
          {
            id_propiedad: '550e8400-e29b-41d4-a716-446655440000',
            id_categoria: '550e8400-e29b-41d4-a716-446655440010',
            propiedad_nombre: 'Hotel',
            categoria_nombre: 'Bordeaux Getaway',
            imagen_principal_url: 'https://example.com/img.jpg',
            amenidades_destacadas: ['Wifi'],
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
          },
        ],
        total: 1,
      };

      let result: { total: number } | undefined;
      service.searchHospedajes(mockRequest).subscribe(r => (result = r));

      const req = httpTesting.expectOne(r => r.url.endsWith('/v1/search'));
      req.flush(mockResponse);

      expect(result?.total).toBe(1);
    });
  });
});
