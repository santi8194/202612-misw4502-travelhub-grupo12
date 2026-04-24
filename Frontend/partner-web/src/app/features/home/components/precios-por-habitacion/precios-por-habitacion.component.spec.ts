import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SimpleChange } from '@angular/core';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { of, EMPTY, throwError } from 'rxjs';
import { PreciosPorHabitacionComponent } from './precios-por-habitacion.component';
import { CatalogService } from '../../../../core/services/catalog.service';
import { TranslateModule } from '@ngx-translate/core';

const mockCatalogService = {
    getCategorias: jasmine.createSpy('getCategorias').and.returnValue(EMPTY),
    getPricing:    jasmine.createSpy('getPricing').and.returnValue(EMPTY),
    updatePricing: jasmine.createSpy('updatePricing').and.returnValue(EMPTY),
};

describe('PreciosPorHabitacionComponent', () => {
  let component: PreciosPorHabitacionComponent;
  let fixture: ComponentFixture<PreciosPorHabitacionComponent>;

  beforeEach(async () => {
    mockCatalogService.getCategorias.calls.reset();
    mockCatalogService.getPricing.calls.reset();
    mockCatalogService.updatePricing.calls.reset();
    mockCatalogService.getCategorias.and.returnValue(EMPTY);
    mockCatalogService.getPricing.and.returnValue(EMPTY);
    mockCatalogService.updatePricing.and.returnValue(EMPTY);

    await TestBed.configureTestingModule({
      imports: [PreciosPorHabitacionComponent, TranslateModule.forRoot()],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: CatalogService, useValue: mockCatalogService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(PreciosPorHabitacionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // â”€â”€â”€ Creation â”€â”€â”€

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should have 4 room type rows', () => {
    expect(component.filas.length).toBe(4);
  });

  it('should start with valid data', () => {
    expect(component.isValid()).toBeTrue();
  });

  // â”€â”€â”€ Carga desde catÃ¡logo â”€â”€â”€

  it('should call getCategorias when idPropiedad changes', () => {
    mockCatalogService.getCategorias.and.returnValue(of({ id_propiedad: 'p1', total_categorias: 0, categorias: [] }));
    component.idPropiedad = 'p1';
    component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
    expect(mockCatalogService.getCategorias).toHaveBeenCalledWith('p1');
  });

  it('should not call getCategorias when idPropiedad is null', () => {
    mockCatalogService.getCategorias.calls.reset();
    component.idPropiedad = null;
    component.ngOnChanges({ idPropiedad: new SimpleChange('p1', null, false) });
    expect(mockCatalogService.getCategorias).not.toHaveBeenCalled();
  });

  it('should load filas from catalog response', () => {
    const cat = { id_categoria: 'cat-1', nombre_comercial: 'EstÃ¡ndar', precio_base: { monto: '200000', moneda: 'COP', cargo_servicio: '0' }, capacidad_pax: 2 };
    const pricing = { id_categoria: 'cat-1', nombre_comercial: 'EstÃ¡ndar', tarifa_base: { monto: '200000', moneda: 'COP', cargo_servicio: '0' }, tarifa_fin_de_semana: { monto: '240000', moneda: 'COP', cargo_servicio: '0' }, tarifa_temporada_alta: { monto: '300000', moneda: 'COP', cargo_servicio: '0' } };
    mockCatalogService.getCategorias.and.returnValue(of({ id_propiedad: 'p1', total_categorias: 1, categorias: [cat] }));
    mockCatalogService.getPricing.and.returnValue(of(pricing));

    component.idPropiedad = 'p1';
    component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });

    expect(component.filas.length).toBe(1);
    expect(component.filas[0].tarifaBase).toBe(200000);
    expect(component.filas[0].tarifaFinDeSemana).toBe(240000);
    expect(component.filas[0].tarifaTemporadaAlta).toBe(300000);
    expect(component.filas[0].idCategoria).toBe('cat-1');
  });

  it('should keep default rows when catalog returns empty categories', () => {
    mockCatalogService.getCategorias.and.returnValue(of({ id_propiedad: 'p1', total_categorias: 0, categorias: [] }));
    component.idPropiedad = 'p1';
    component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
    expect(component.filas.length).toBe(4);
  });

  it('should set loadError on getCategorias failure', () => {
    mockCatalogService.getCategorias.and.returnValue(throwError(() => new Error('Network error')));
    component.idPropiedad = 'p-error';
    component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p-error', true) });
    expect(component.loadError).toBeTrue();
  });

  // â”€â”€â”€ save() â”€â”€â”€

  it('save should return false when validation fails', () => {
    component.filas[0].tarifaBase = null;
    component.filas[0].errores = {};
    let result: boolean | undefined;
    component.save().subscribe(v => result = v);
    expect(result).toBeFalse();
  });

  it('save should succeed locally when no idCategoria (fallback rows)', () => {
    component.idPropiedad = null;
    let result: boolean | undefined;
    component.save().subscribe(v => result = v);
    expect(result).toBeTrue();
    expect(component.saveSuccess).toBeTrue();
  });

  it('save should call updatePricing for each row with idCategoria', () => {
    mockCatalogService.updatePricing.and.returnValue(of({ ok: true }));
    component.idPropiedad = 'prop-1';
    component.filas = [
      { idCategoria: 'cat-1', moneda: 'COP', cargoServicio: '0', tipoHabitacion: 'EstÃ¡ndar', totalHabitaciones: 2, tarifaBase: 100, tarifaFinDeSemana: 120, tarifaTemporadaAlta: 150, variacionFinDeSemana: '+20%', variacionTemporadaAlta: '+50%', errores: {} },
    ];
    let result: boolean | undefined;
    component.save().subscribe(v => result = v);
    expect(mockCatalogService.updatePricing).toHaveBeenCalledWith('prop-1', 'cat-1', jasmine.any(Object));
    expect(result).toBeTrue();
    expect(component.saveSuccess).toBeTrue();
  });

  it('save should set saveError when updatePricing fails', () => {
    mockCatalogService.updatePricing.and.returnValue(throwError(() => new Error('error')));
    component.idPropiedad = 'prop-1';
    component.filas = [
      { idCategoria: 'cat-1', moneda: 'COP', cargoServicio: '0', tipoHabitacion: 'EstÃ¡ndar', totalHabitaciones: 2, tarifaBase: 100, tarifaFinDeSemana: 120, tarifaTemporadaAlta: 150, variacionFinDeSemana: '+20%', variacionTemporadaAlta: '+50%', errores: {} },
    ];
    let result: boolean | undefined;
    component.save().subscribe(v => result = v);
    expect(result).toBeFalse();
    expect(component.saveError).toBeTrue();
  });

  // â”€â”€â”€ onPriceInput: empty value â”€â”€â”€

  it('should set REQUIRED error when input is empty', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '');
    expect(fila.tarifaBase).toBeNull();
    expect(fila.errores['tarifaBase']).toBe('PRICING_VALIDATION.REQUIRED');
  });

  it('should set REQUIRED error when input is whitespace only', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '   ');
    expect(fila.tarifaBase).toBeNull();
    expect(fila.errores['tarifaBase']).toBe('PRICING_VALIDATION.REQUIRED');
  });

  // â”€â”€â”€ onPriceInput: non-numeric â”€â”€â”€

  it('should set NUMERIC error for non-numeric input', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', 'abc');
    expect(fila.tarifaBase).toBeNull();
    expect(fila.errores['tarifaBase']).toBe('PRICING_VALIDATION.NUMERIC');
  });

  it('should set NUMERIC error for mixed text', () => {
    const fila = component.filas[1];
    component.onPriceInput(fila, 'tarifaFinDeSemana', '12x');
    expect(fila.tarifaFinDeSemana).toBeNull();
    expect(fila.errores['tarifaFinDeSemana']).toBe('PRICING_VALIDATION.NUMERIC');
  });

  // â”€â”€â”€ onPriceInput: zero or negative â”€â”€â”€

  it('should set POSITIVE error for zero', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '0');
    expect(fila.tarifaBase).toBeNull();
    expect(fila.errores['tarifaBase']).toBe('PRICING_VALIDATION.POSITIVE');
  });

  it('should set POSITIVE error for negative number', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaTemporadaAlta', '-50');
    expect(fila.tarifaTemporadaAlta).toBeNull();
    expect(fila.errores['tarifaTemporadaAlta']).toBe('PRICING_VALIDATION.POSITIVE');
  });

  // â”€â”€â”€ onPriceInput: valid value â”€â”€â”€

  it('should accept valid positive number and clear error', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', 'abc');
    expect(fila.errores['tarifaBase']).toBeTruthy();
    component.onPriceInput(fila, 'tarifaBase', '250');
    expect(fila.tarifaBase).toBe(250);
    expect(fila.errores['tarifaBase']).toBeUndefined();
  });

  it('should accept decimal numbers', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '99.50');
    expect(fila.tarifaBase).toBe(99.50);
    expect(fila.errores['tarifaBase']).toBeUndefined();
  });

  // â”€â”€â”€ onPriceInput: emits validityChange â”€â”€â”€

  it('should emit validityChange true when all values are valid', () => {
    let emittedValue: boolean | undefined;
    component.validityChange.subscribe(v => emittedValue = v);
    component.onPriceInput(component.filas[0], 'tarifaBase', '100');
    expect(emittedValue).toBeTrue();
  });

  it('should emit validityChange false when a value is invalid', () => {
    let emittedValue: boolean | undefined;
    component.validityChange.subscribe(v => emittedValue = v);
    component.onPriceInput(component.filas[0], 'tarifaBase', '');
    expect(emittedValue).toBeFalse();
  });

  // â”€â”€â”€ recalcularVariaciones â”€â”€â”€

  it('should recalculate weekend variation when base and weekend are valid', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '100');
    component.onPriceInput(fila, 'tarifaFinDeSemana', '150');
    expect(fila.variacionFinDeSemana).toBe('+50%');
  });

  it('should recalculate peak variation when base and peak are valid', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '200');
    component.onPriceInput(fila, 'tarifaTemporadaAlta', '300');
    expect(fila.variacionTemporadaAlta).toBe('+50%');
  });

  it('should show negative variation when rate is lower than base', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '200');
    component.onPriceInput(fila, 'tarifaFinDeSemana', '100');
    expect(fila.variacionFinDeSemana).toBe('-50%');
  });

  it('should clear weekend variation when weekend is invalid', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '100');
    component.onPriceInput(fila, 'tarifaFinDeSemana', '');
    expect(fila.variacionFinDeSemana).toBe('');
  });

  it('should clear peak variation when peak is invalid', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '100');
    component.onPriceInput(fila, 'tarifaTemporadaAlta', 'abc');
    expect(fila.variacionTemporadaAlta).toBe('');
  });

  it('should clear both variations when base is invalid', () => {
    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '');
    expect(fila.variacionFinDeSemana).toBe('');
    expect(fila.variacionTemporadaAlta).toBe('');
  });

  // â”€â”€â”€ isValid â”€â”€â”€

  it('isValid should return false when any field has error', () => {
    component.onPriceInput(component.filas[2], 'tarifaBase', 'bad');
    expect(component.isValid()).toBeFalse();
  });

  it('isValid should return false when any field is null', () => {
    component.filas[0].tarifaBase = null;
    component.filas[0].errores = {};
    expect(component.isValid()).toBeFalse();
  });

  // â”€â”€â”€ validate â”€â”€â”€

  it('validate should return true when all data is valid', () => {
    expect(component.validate()).toBeTrue();
  });

  it('validate should mark null fields as REQUIRED', () => {
    component.filas[0].tarifaBase = null;
    component.filas[0].errores = {};
    const result = component.validate();
    expect(result).toBeFalse();
    expect(component.filas[0].errores['tarifaBase']).toBe('PRICING_VALIDATION.REQUIRED');
  });

  it('validate should not overwrite existing error on null field', () => {
    component.filas[0].tarifaBase = null;
    component.filas[0].errores = { tarifaBase: 'PRICING_VALIDATION.NUMERIC' };
    component.validate();
    expect(component.filas[0].errores['tarifaBase']).toBe('PRICING_VALIDATION.NUMERIC');
  });

  // â”€â”€â”€ Template rendering â”€â”€â”€

  it('should render inputs for each room row', () => {
    const inputs = fixture.nativeElement.querySelectorAll('.fila-datos input');
    // 4 rows x 3 inputs each = 12
    expect(inputs.length).toBe(12);
  });

  it('should display error message when field has error', () => {
    component.onPriceInput(component.filas[0], 'tarifaBase', '');
    fixture.detectChanges();
    const errorMsgs = fixture.nativeElement.querySelectorAll('.error-msg');
    expect(errorMsgs.length).toBeGreaterThan(0);
  });

  it('should add input-error class when field has error', () => {
    component.onPriceInput(component.filas[0], 'tarifaBase', 'abc');
    fixture.detectChanges();
    const errorInputs = fixture.nativeElement.querySelectorAll('.input-error');
    expect(errorInputs.length).toBeGreaterThan(0);
  });

  it('should show variation when no error and variation exists', () => {
    fixture.detectChanges();
    const variations = fixture.nativeElement.querySelectorAll('.variacion');
    expect(variations.length).toBeGreaterThan(0);
  });

  it('should hide variation when field has error', () => {
    component.onPriceInput(component.filas[0], 'tarifaFinDeSemana', 'bad');
    fixture.detectChanges();
    const row = fixture.nativeElement.querySelectorAll('.fila-datos')[0];
    const weekendCol = row.querySelectorAll('.precio-columna')[1];
    const weekendVar = weekendCol?.querySelector('.variacion');
    expect(weekendVar).toBeNull();
  });
});
