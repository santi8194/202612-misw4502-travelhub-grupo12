import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { forkJoin, Observable, of } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';
import { CatalogService, PricingUpdate } from '../../../../core/services/catalog.service';

export interface FilaPrecioHabitacion {
    idCategoria: string;
    moneda: string;
    cargoServicio: string;
    tipoHabitacion: string;
    totalHabitaciones: number;
    tarifaBase: number | null;
    tarifaFinDeSemana: number | null;
    tarifaTemporadaAlta: number | null;
    variacionFinDeSemana: string;
    variacionTemporadaAlta: string;
    errores: Record<string, string>;
}

// Filas precargadas con valores válidos (se muestran cuando no hay categorías del backend)
const FILAS_DEFECTO: FilaPrecioHabitacion[] = [
    { idCategoria: '', moneda: 'COP', cargoServicio: '0', tipoHabitacion: 'Habitacion Estandar',  totalHabitaciones: 20, tarifaBase: 100, tarifaFinDeSemana: 120, tarifaTemporadaAlta: 150, variacionFinDeSemana: '+20%', variacionTemporadaAlta: '+50%', errores: {} },
    { idCategoria: '', moneda: 'COP', cargoServicio: '0', tipoHabitacion: 'Suite Deluxe',          totalHabitaciones: 10, tarifaBase: 200, tarifaFinDeSemana: 240, tarifaTemporadaAlta: 300, variacionFinDeSemana: '+20%', variacionTemporadaAlta: '+50%', errores: {} },
    { idCategoria: '', moneda: 'COP', cargoServicio: '0', tipoHabitacion: 'Suite Ejecutiva',       totalHabitaciones: 5,  tarifaBase: 350, tarifaFinDeSemana: 420, tarifaTemporadaAlta: 525, variacionFinDeSemana: '+20%', variacionTemporadaAlta: '+50%', errores: {} },
    { idCategoria: '', moneda: 'COP', cargoServicio: '0', tipoHabitacion: 'Suite Presidencial',    totalHabitaciones: 2,  tarifaBase: 500, tarifaFinDeSemana: 600, tarifaTemporadaAlta: 750, variacionFinDeSemana: '+20%', variacionTemporadaAlta: '+50%', errores: {} },
];

@Component({
    selector: 'app-precios-por-habitacion',
    standalone: true,
    imports: [CommonModule, TranslateModule],
    templateUrl: './precios-por-habitacion.component.html',
    styleUrl: './precios-por-habitacion.component.scss'
})
export class PreciosPorHabitacionComponent implements OnInit, OnChanges {
    @Input() idPropiedad: string | null = null;
    @Output() validityChange = new EventEmitter<boolean>();

    filas: FilaPrecioHabitacion[] = [];
    loading = false;
    saving = false;
    saveSuccess = false;
    saveError = false;
    loadError = false;

    constructor(private catalogService: CatalogService) {}

    ngOnInit(): void {
        // Siempre mostrar filas con datos por defecto hasta que lleguen los datos del API
        this.filas = FILAS_DEFECTO.map(f => ({ ...f, errores: {} }));
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['idPropiedad'] && this.idPropiedad) {
            this.cargarDesdeCatalog();
        }
    }

    private cargarDesdeCatalog(): void {
        if (!this.idPropiedad) return;
        this.loading = true;
        this.loadError = false;

        this.catalogService.getCategorias(this.idPropiedad).pipe(
            switchMap(resp => {
                const categorias = resp.categorias ?? [];
                if (categorias.length === 0) return of([]);
                const pricingRequests = categorias.map(cat =>
                    this.catalogService.getPricing(this.idPropiedad!, cat.id_categoria).pipe(
                        catchError(() => of(null))
                    )
                );
                return forkJoin(pricingRequests).pipe(
                    map(pricings => categorias.map((cat, i) => ({ cat, pricing: pricings[i] })))
                );
            }),
            catchError(() => {
                this.loadError = true;
                this.loading = false;
                return of([]);
            })
        ).subscribe(items => {
            this.loading = false;
            const loaded = (items as Array<{ cat: any; pricing: any }>).map(({ cat, pricing }) => {
                const base = pricing?.tarifa_base ?? cat.precio_base;
                const fw   = pricing?.tarifa_fin_de_semana ?? null;
                const ha   = pricing?.tarifa_temporada_alta ?? null;
                const fila: FilaPrecioHabitacion = {
                    idCategoria:          cat.id_categoria,
                    moneda:               base?.moneda ?? 'COP',
                    cargoServicio:        base?.cargo_servicio ?? '0',
                    tipoHabitacion:       cat.nombre_comercial,
                    totalHabitaciones:    cat.capacidad_pax ?? 0,
                    tarifaBase:           base  ? parseFloat(base.monto)  : null,
                    tarifaFinDeSemana:    fw    ? parseFloat(fw.monto)    : null,
                    tarifaTemporadaAlta:  ha    ? parseFloat(ha.monto)    : null,
                    variacionFinDeSemana: '',
                    variacionTemporadaAlta: '',
                    errores: {},
                };
                this.recalcularVariaciones(fila);
                return fila;
            });
            if (loaded.length > 0) {
                this.filas = loaded;
            }
            this.validityChange.emit(this.isValid());
        });
    }

    save(): Observable<boolean> {
        if (!this.validate()) {
            return of(false);
        }
        const filasConId = this.filas.filter(f => f.idCategoria && this.idPropiedad);
        if (filasConId.length === 0) {
            this.saveSuccess = true;
            setTimeout(() => (this.saveSuccess = false), 3000);
            return of(true);
        }
        this.saving = true;
        this.saveSuccess = false;
        this.saveError = false;

        const requests = filasConId.map(fila => {
            const body: PricingUpdate = {
                tarifa_base_monto:             String(fila.tarifaBase!),
                moneda:                        fila.moneda,
                cargo_servicio:                fila.cargoServicio,
                tarifa_fin_de_semana_monto:    fila.tarifaFinDeSemana  != null ? String(fila.tarifaFinDeSemana)  : null,
                tarifa_temporada_alta_monto:   fila.tarifaTemporadaAlta != null ? String(fila.tarifaTemporadaAlta) : null,
            };
            return this.catalogService.updatePricing(this.idPropiedad!, fila.idCategoria, body).pipe(
                catchError(() => of(null))
            );
        });

        return forkJoin(requests).pipe(
            map(results => {
                this.saving = false;
                const anyError = results.some(r => r === null);
                if (anyError) {
                    this.saveError = true;
                    return false;
                }
                this.saveSuccess = true;
                setTimeout(() => (this.saveSuccess = false), 3000);
                return true;
            }),
            catchError(() => {
                this.saving = false;
                this.saveError = true;
                return of(false);
            })
        );
    }

    onPriceInput(fila: FilaPrecioHabitacion, campo: 'tarifaBase' | 'tarifaFinDeSemana' | 'tarifaTemporadaAlta', rawValue: string): void {
        const trimmed = rawValue.trim();
        if (trimmed === '') {
            fila[campo] = null;
            fila.errores[campo] = 'PRICING_VALIDATION.REQUIRED';
        } else {
            const num = Number(trimmed);
            if (isNaN(num)) {
                fila[campo] = null;
                fila.errores[campo] = 'PRICING_VALIDATION.NUMERIC';
            } else if (num <= 0) {
                fila[campo] = null;
                fila.errores[campo] = 'PRICING_VALIDATION.POSITIVE';
            } else {
                fila[campo] = num;
                delete fila.errores[campo];
            }
        }
        this.recalcularVariaciones(fila);
        this.validityChange.emit(this.isValid());
    }

    isValid(): boolean {
        return this.filas.every(f => Object.keys(f.errores).length === 0
            && f.tarifaBase !== null
            && f.tarifaFinDeSemana !== null
            && f.tarifaTemporadaAlta !== null);
    }

    validate(): boolean {
        for (const fila of this.filas) {
            for (const campo of ['tarifaBase', 'tarifaFinDeSemana', 'tarifaTemporadaAlta'] as const) {
                if (fila[campo] === null || fila[campo] === undefined) {
                    if (!fila.errores[campo]) {
                        fila.errores[campo] = 'PRICING_VALIDATION.REQUIRED';
                    }
                }
            }
        }
        return this.isValid();
    }

    private recalcularVariaciones(fila: FilaPrecioHabitacion): void {
        if (fila.tarifaBase && fila.tarifaBase > 0) {
            if (fila.tarifaFinDeSemana && fila.tarifaFinDeSemana > 0) {
                const pct = ((fila.tarifaFinDeSemana - fila.tarifaBase) / fila.tarifaBase) * 100;
                fila.variacionFinDeSemana = `${pct >= 0 ? '+' : ''}${Math.round(pct)}%`;
            } else {
                fila.variacionFinDeSemana = '';
            }
            if (fila.tarifaTemporadaAlta && fila.tarifaTemporadaAlta > 0) {
                const pct = ((fila.tarifaTemporadaAlta - fila.tarifaBase) / fila.tarifaBase) * 100;
                fila.variacionTemporadaAlta = `${pct >= 0 ? '+' : ''}${Math.round(pct)}%`;
            } else {
                fila.variacionTemporadaAlta = '';
            }
        } else {
            fila.variacionFinDeSemana = '';
            fila.variacionTemporadaAlta = '';
        }
    }
}
