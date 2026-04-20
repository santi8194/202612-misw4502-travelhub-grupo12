import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

interface FilaPrecioHabitacion {
    tipoHabitacion: string;
    totalHabitaciones: number;
    tarifaBase: number | null;
    tarifaFinDeSemana: number | null;
    tarifaTemporadaAlta: number | null;
    variacionFinDeSemana: string;
    variacionTemporadaAlta: string;
    errores: Record<string, string>;
}

@Component({
    selector: 'app-precios-por-habitacion',
    standalone: true,
    imports: [CommonModule, TranslateModule],
    templateUrl: './precios-por-habitacion.component.html',
    styleUrl: './precios-por-habitacion.component.scss'
})
export class PreciosPorHabitacionComponent {
    @Output() validityChange = new EventEmitter<boolean>();

    filas: FilaPrecioHabitacion[] = [
        {
            tipoHabitacion: 'Habitacion Estandar',
            totalHabitaciones: 20,
            tarifaBase: 100,
            tarifaFinDeSemana: 120,
            tarifaTemporadaAlta: 150,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%',
            errores: {}
        },
        {
            tipoHabitacion: 'Suite Deluxe',
            totalHabitaciones: 10,
            tarifaBase: 200,
            tarifaFinDeSemana: 240,
            tarifaTemporadaAlta: 300,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%',
            errores: {}
        },
        {
            tipoHabitacion: 'Suite Ejecutiva',
            totalHabitaciones: 5,
            tarifaBase: 350,
            tarifaFinDeSemana: 420,
            tarifaTemporadaAlta: 525,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%',
            errores: {}
        },
        {
            tipoHabitacion: 'Suite Presidencial',
            totalHabitaciones: 2,
            tarifaBase: 500,
            tarifaFinDeSemana: 600,
            tarifaTemporadaAlta: 750,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%',
            errores: {}
        }
    ];

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
