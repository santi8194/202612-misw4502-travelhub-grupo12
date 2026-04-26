import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SimpleChange } from '@angular/core';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { of, EMPTY, throwError } from 'rxjs';
import { AjustesTemporadaComponent } from './ajustes-temporada.component';
import { CatalogService } from '../../../../core/services/catalog.service';
import { TranslateModule } from '@ngx-translate/core';

const TEMPORADAS_MOCK = [
    { id_temporada: 't1', nombre: 'Verano', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 },
    { id_temporada: 't2', nombre: 'Navidad', fecha_inicio: '2026-12-15', fecha_fin: '2027-01-05', porcentaje: 40 },
];

const mockCatalogService = {
    getTemporadas:    jasmine.createSpy('getTemporadas').and.returnValue(EMPTY),
    createTemporada:  jasmine.createSpy('createTemporada').and.returnValue(EMPTY),
    deleteTemporada:  jasmine.createSpy('deleteTemporada').and.returnValue(EMPTY),
};

describe('AjustesTemporadaComponent', () => {
    let component: AjustesTemporadaComponent;
    let fixture: ComponentFixture<AjustesTemporadaComponent>;

    beforeEach(async () => {
        mockCatalogService.getTemporadas.calls.reset();
        mockCatalogService.createTemporada.calls.reset();
        mockCatalogService.deleteTemporada.calls.reset();
        mockCatalogService.getTemporadas.and.returnValue(EMPTY);
        mockCatalogService.createTemporada.and.returnValue(EMPTY);
        mockCatalogService.deleteTemporada.and.returnValue(EMPTY);

        await TestBed.configureTestingModule({
            imports: [AjustesTemporadaComponent, TranslateModule.forRoot()],
            providers: [
                provideHttpClient(),
                provideHttpClientTesting(),
                { provide: CatalogService, useValue: mockCatalogService },
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(AjustesTemporadaComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    // ─── Creation ───

    it('should create the component', () => {
        expect(component).toBeTruthy();
    });

    it('should start with empty temporadas list', () => {
        expect(component.temporadas.length).toBe(0);
    });

    it('should not show form by default', () => {
        expect(component.showForm).toBeFalse();
    });

    // ─── Loading ───

    it('should call getTemporadas when idPropiedad is set', () => {
        mockCatalogService.getTemporadas.and.returnValue(
            of({ id_propiedad: 'p1', temporadas: TEMPORADAS_MOCK })
        );
        component.idPropiedad = 'p1';
        component.ngOnChanges({
            idPropiedad: new SimpleChange(null, 'p1', true),
        });
        expect(mockCatalogService.getTemporadas).toHaveBeenCalledWith('p1');
        expect(component.temporadas.length).toBe(2);
    });

    it('should set loadError on getTemporadas failure', () => {
        mockCatalogService.getTemporadas.and.returnValue(throwError(() => new Error('fail')));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.loadError).toBeTrue();
    });

    it('should not call getTemporadas if idPropiedad is null', () => {
        component.idPropiedad = null;
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, null, true) });
        expect(mockCatalogService.getTemporadas).not.toHaveBeenCalled();
    });

    // ─── Template rendering ───

    it('should render temporada items', () => {
        component.temporadas = TEMPORADAS_MOCK;
        fixture.detectChanges();
        const items = fixture.nativeElement.querySelectorAll('[data-testid="temporada-item"]');
        expect(items.length).toBe(2);
    });

    it('should display the name and percentage of each temporada', () => {
        component.temporadas = [TEMPORADAS_MOCK[0]];
        fixture.detectChanges();
        const nombre = fixture.nativeElement.querySelector('[data-testid="temporada-nombre"]');
        const pct    = fixture.nativeElement.querySelector('[data-testid="temporada-pct"]');
        expect(nombre.textContent).toContain('Verano');
        expect(pct.textContent).toContain('25');
    });

    it('should show empty message when no temporadas', () => {
        component.temporadas = [];
        fixture.detectChanges();
        const vacio = fixture.nativeElement.querySelector('[data-testid="temporadas-vacio"]');
        expect(vacio).toBeTruthy();
    });

    it('should show form when openForm() is called', () => {
        component.openForm();
        fixture.detectChanges();
        const form = fixture.nativeElement.querySelector('[data-testid="form-temporada"]');
        expect(form).toBeTruthy();
    });

    it('should hide form when cancelForm() is called', () => {
        component.openForm();
        component.cancelForm();
        fixture.detectChanges();
        const form = fixture.nativeElement.querySelector('[data-testid="form-temporada"]');
        expect(form).toBeFalsy();
    });

    // ─── Palette helpers ───

    it('colorBg should cycle through palette', () => {
        const bg0 = component.colorBg(0);
        const bg6 = component.colorBg(6);   // same as 0 (modulo 6)
        expect(bg0).toBe(bg6);
    });

    it('colorText should cycle through palette', () => {
        const t0 = component.colorText(0);
        const t6 = component.colorText(6);
        expect(t0).toBe(t6);
    });

    // ─── formatDate ───

    it('formatDate should return short month and day', () => {
        const result = component.formatDate('2026-06-01');
        expect(result).toContain('Jun');
        expect(result).toContain('1');
    });

    // ─── Validation ───

    it('should fail validation when nombre is empty', () => {
        component.openForm();
        component.form = { nombre: '', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 };
        component.guardar();
        expect(component.formErrors['nombre']).toBeTruthy();
    });

    it('should fail validation when fecha_fin is before fecha_inicio', () => {
        component.openForm();
        component.form = { nombre: 'Test', fecha_inicio: '2026-08-31', fecha_fin: '2026-06-01', porcentaje: 25 };
        component.guardar();
        expect(component.formErrors['fecha_fin']).toBeTruthy();
    });

    it('should fail validation when porcentaje is zero', () => {
        component.openForm();
        component.form = { nombre: 'Test', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 0 };
        component.guardar();
        expect(component.formErrors['porcentaje']).toBeTruthy();
    });

    // ─── Save ───

    it('should call createTemporada on valid guardar()', () => {
        const nueva = { id_temporada: 't3', nombre: 'Verano', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 };
        mockCatalogService.createTemporada.and.returnValue(of(nueva));
        component.idPropiedad = 'p1';
        component.openForm();
        component.form = { nombre: 'Verano', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 };
        component.guardar();
        expect(mockCatalogService.createTemporada).toHaveBeenCalledWith('p1', component.form);
        expect(component.temporadas).toContain(nueva);
        expect(component.showForm).toBeFalse();
    });

    it('should set saveError on createTemporada failure', () => {
        mockCatalogService.createTemporada.and.returnValue(throwError(() => new Error('fail')));
        component.idPropiedad = 'p1';
        component.openForm();
        component.form = { nombre: 'Verano', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 };
        component.guardar();
        expect(component.saveError).toBeTrue();
    });

    it('should not call createTemporada when idPropiedad is null', () => {
        component.idPropiedad = null;
        component.openForm();
        component.form = { nombre: 'Verano', fecha_inicio: '2026-06-01', fecha_fin: '2026-08-31', porcentaje: 25 };
        component.guardar();
        expect(mockCatalogService.createTemporada).not.toHaveBeenCalled();
    });

    // ─── Delete ───

    it('should call deleteTemporada and remove from list', () => {
        mockCatalogService.deleteTemporada.and.returnValue(of({ deleted: true }));
        component.idPropiedad = 'p1';
        component.temporadas = [...TEMPORADAS_MOCK];
        component.eliminar('t1');
        expect(mockCatalogService.deleteTemporada).toHaveBeenCalledWith('p1', 't1');
        expect(component.temporadas.find(t => t.id_temporada === 't1')).toBeUndefined();
    });

    it('should not call deleteTemporada when idPropiedad is null', () => {
        component.idPropiedad = null;
        component.temporadas = [...TEMPORADAS_MOCK];
        component.eliminar('t1');
        expect(mockCatalogService.deleteTemporada).not.toHaveBeenCalled();
    });

    it('should handle deleteTemporada error gracefully', () => {
        mockCatalogService.deleteTemporada.and.returnValue(throwError(() => new Error('fail')));
        component.idPropiedad = 'p1';
        component.temporadas = [...TEMPORADAS_MOCK];
        // should not throw
        expect(() => component.eliminar('t1')).not.toThrow();
    });
});
