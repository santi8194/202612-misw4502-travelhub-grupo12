import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { CatalogService, PricingUpdate, CategoriasResponse, PricingResponse, TemporadasResponse, TemporadaApi } from './catalog.service';
import { environment } from '../../../environments/environment';

describe('CatalogService', () => {
    let service: CatalogService;
    let httpMock: HttpTestingController;

    const base = environment.catalogApiUrl;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                CatalogService,
                provideHttpClient(),
                provideHttpClientTesting(),
            ],
        });
        service = TestBed.inject(CatalogService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    // ─── getCategorias ───

    describe('getCategorias', () => {
        it('should GET categories for a propiedad', () => {
            const mockResponse: CategoriasResponse = {
                id_propiedad: 'p1',
                total_categorias: 1,
                categorias: [
                    {
                        id_categoria: 'cat-1',
                        nombre_comercial: 'Estándar',
                        precio_base: { monto: '200000', moneda: 'COP', cargo_servicio: '0' },
                        capacidad_pax: 2,
                    },
                ],
            };

            service.getCategorias('p1').subscribe((res) => {
                expect(res.id_propiedad).toBe('p1');
                expect(res.total_categorias).toBe(1);
                expect(res.categorias[0].id_categoria).toBe('cat-1');
            });

            const req = httpMock.expectOne(`${base}/properties/p1/categories`);
            expect(req.request.method).toBe('GET');
            req.flush(mockResponse);
        });

        it('should return empty categories list when none exist', () => {
            const mockEmpty: CategoriasResponse = { id_propiedad: 'p-empty', total_categorias: 0, categorias: [] };

            service.getCategorias('p-empty').subscribe((res) => {
                expect(res.categorias).toEqual([]);
            });

            httpMock.expectOne(`${base}/properties/p-empty/categories`).flush(mockEmpty);
        });
    });

    // ─── getPricing ───

    describe('getPricing', () => {
        it('should GET pricing for a category', () => {
            const mockResponse: PricingResponse = {
                id_categoria: 'cat-1',
                nombre_comercial: 'Estándar',
                tarifa_base: { monto: '200000', moneda: 'COP', cargo_servicio: '0' },
                tarifa_fin_de_semana: { monto: '240000', moneda: 'COP', cargo_servicio: '0' },
                tarifa_temporada_alta: { monto: '300000', moneda: 'COP', cargo_servicio: '0' },
            };

            service.getPricing('p1', 'cat-1').subscribe((res) => {
                expect(res.id_categoria).toBe('cat-1');
                expect(res.tarifa_base?.monto).toBe('200000');
            });

            const req = httpMock.expectOne(`${base}/properties/p1/categories/cat-1/pricing`);
            expect(req.request.method).toBe('GET');
            req.flush(mockResponse);
        });

        it('should handle null pricing fields', () => {
            const mockNull: PricingResponse = {
                id_categoria: 'cat-2',
                nombre_comercial: 'Suite',
                tarifa_base: null,
                tarifa_fin_de_semana: null,
                tarifa_temporada_alta: null,
            };

            service.getPricing('p1', 'cat-2').subscribe((res) => {
                expect(res.tarifa_base).toBeNull();
            });

            httpMock.expectOne(`${base}/properties/p1/categories/cat-2/pricing`).flush(mockNull);
        });
    });

    // ─── updatePricing ───

    describe('updatePricing', () => {
        it('should PUT pricing for a category', () => {
            const body: PricingUpdate = {
                tarifa_base_monto: '200000',
                moneda: 'COP',
                cargo_servicio: '0',
                tarifa_fin_de_semana_monto: '240000',
                tarifa_temporada_alta_monto: '300000',
            };

            service.updatePricing('p1', 'cat-1', body).subscribe((res) => {
                expect(res).toBeTruthy();
            });

            const req = httpMock.expectOne(`${base}/properties/p1/categories/cat-1/pricing`);
            expect(req.request.method).toBe('PUT');
            expect(req.request.body).toEqual(body);
            req.flush({ success: true });
        });

        it('should send null weekend and peak rates when not provided', () => {
            const body: PricingUpdate = {
                tarifa_base_monto: '150000',
                moneda: 'COP',
                cargo_servicio: '0',
                tarifa_fin_de_semana_monto: null,
                tarifa_temporada_alta_monto: null,
            };

            service.updatePricing('p1', 'cat-2', body).subscribe();

            const req = httpMock.expectOne(`${base}/properties/p1/categories/cat-2/pricing`);
            expect(req.request.body.tarifa_fin_de_semana_monto).toBeNull();
            expect(req.request.body.tarifa_temporada_alta_monto).toBeNull();
            req.flush({});
        });
    });

    // ─── getTemporadas ───

    describe('getTemporadas', () => {
        it('should GET temporadas for a propiedad', () => {
            const mockResponse: TemporadasResponse = {
                id_propiedad: 'p1',
                temporadas: [
                    { id_temporada: 't1', nombre: 'Verano', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 },
                ],
            };

            service.getTemporadas('p1').subscribe((res) => {
                expect(res.id_propiedad).toBe('p1');
                expect(res.temporadas.length).toBe(1);
            });

            const req = httpMock.expectOne(`${base}/properties/p1/seasons`);
            expect(req.request.method).toBe('GET');
            req.flush(mockResponse);
        });

        it('should return empty list when no temporadas exist', () => {
            const mockEmpty: TemporadasResponse = { id_propiedad: 'p2', temporadas: [] };

            service.getTemporadas('p2').subscribe((res) => {
                expect(res.temporadas).toEqual([]);
            });

            httpMock.expectOne(`${base}/properties/p2/seasons`).flush(mockEmpty);
        });
    });

    // ─── createTemporada ───

    describe('createTemporada', () => {
        it('should POST a new temporada', () => {
            const body = { nombre: 'Verano', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 };
            const mockCreated: TemporadaApi = { id_temporada: 't1', ...body };

            service.createTemporada('p1', body).subscribe((res) => {
                expect(res.id_temporada).toBe('t1');
                expect(res.nombre).toBe('Verano');
                expect(res.porcentaje).toBe(25);
            });

            const req = httpMock.expectOne(`${base}/properties/p1/seasons`);
            expect(req.request.method).toBe('POST');
            expect(req.request.body).toEqual(body);
            req.flush(mockCreated);
        });
    });

    // ─── deleteTemporada ───

    describe('deleteTemporada', () => {
        it('should DELETE a temporada by id', () => {
            service.deleteTemporada('p1', 't1').subscribe((res) => {
                expect(res).toBeTruthy();
            });

            const req = httpMock.expectOne(`${base}/properties/p1/seasons/t1`);
            expect(req.request.method).toBe('DELETE');
            req.flush({ deleted: true });
        });

        it('should DELETE the correct temporada', () => {
            service.deleteTemporada('p1', 't2').subscribe();

            const req = httpMock.expectOne(`${base}/properties/p1/seasons/t2`);
            expect(req.request.url).toContain('t2');
            req.flush({});
        });
    });
});
