import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PreciosPorHabitacionComponent } from './precios-por-habitacion.component';
import { TranslateModule } from '@ngx-translate/core';

describe('PreciosPorHabitacionComponent', () => {
  let component: PreciosPorHabitacionComponent;
  let fixture: ComponentFixture<PreciosPorHabitacionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PreciosPorHabitacionComponent, TranslateModule.forRoot()],
    }).compileComponents();

    fixture = TestBed.createComponent(PreciosPorHabitacionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // ─── Creation ───

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should have 4 room type rows', () => {
    expect(component.filas.length).toBe(4);
  });

  it('should start with valid data', () => {
    expect(component.isValid()).toBeTrue();
  });

  // ─── onPriceInput: empty value ───

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

  // ─── onPriceInput: non-numeric ───

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

  // ─── onPriceInput: zero or negative ───

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

  // ─── onPriceInput: valid value ───

  it('should accept valid positive number and clear error', () => {
    const fila = component.filas[0];
    // First set an error
    component.onPriceInput(fila, 'tarifaBase', 'abc');
    expect(fila.errores['tarifaBase']).toBeTruthy();
    // Then set a valid value
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

  // ─── onPriceInput: emits validityChange ───

  it('should emit validityChange true when all values are valid', () => {
    let emittedValue: boolean | undefined;
    component.validityChange.subscribe(v => emittedValue = v);

    const fila = component.filas[0];
    component.onPriceInput(fila, 'tarifaBase', '100');
    expect(emittedValue).toBeTrue();
  });

  it('should emit validityChange false when a value is invalid', () => {
    let emittedValue: boolean | undefined;
    component.validityChange.subscribe(v => emittedValue = v);

    component.onPriceInput(component.filas[0], 'tarifaBase', '');
    expect(emittedValue).toBeFalse();
  });

  // ─── recalcularVariaciones ───

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

  // ─── isValid ───

  it('isValid should return false when any field has error', () => {
    component.onPriceInput(component.filas[2], 'tarifaBase', 'bad');
    expect(component.isValid()).toBeFalse();
  });

  it('isValid should return false when any field is null', () => {
    component.filas[0].tarifaBase = null;
    component.filas[0].errores = {};
    expect(component.isValid()).toBeFalse();
  });

  // ─── validate ───

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

  // ─── Template rendering ───

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
    const variaciones = row.querySelectorAll('.variacion');
    // Weekend column should not show variation
    const weekendCol = row.querySelectorAll('.precio-columna')[1];
    const weekendVar = weekendCol?.querySelector('.variacion');
    expect(weekendVar).toBeNull();
  });
});
