import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

interface FilaPrecioHabitacion {
    tipoHabitacion: string;
    totalHabitaciones: number;
    tarifaBase: number;
    tarifaFinDeSemana: number;
    tarifaTemporadaAlta: number;
    variacionFinDeSemana: string;
    variacionTemporadaAlta: string;
}

@Component({
    selector: 'app-precios-por-habitacion',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './precios-por-habitacion.component.html',
    styleUrl: './precios-por-habitacion.component.scss'
})
export class PreciosPorHabitacionComponent {
    readonly filas: FilaPrecioHabitacion[] = [
        {
            tipoHabitacion: 'Habitacion Estandar',
            totalHabitaciones: 20,
            tarifaBase: 100,
            tarifaFinDeSemana: 120,
            tarifaTemporadaAlta: 150,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%'
        },
        {
            tipoHabitacion: 'Suite Deluxe',
            totalHabitaciones: 10,
            tarifaBase: 200,
            tarifaFinDeSemana: 240,
            tarifaTemporadaAlta: 300,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%'
        },
        {
            tipoHabitacion: 'Suite Ejecutiva',
            totalHabitaciones: 5,
            tarifaBase: 350,
            tarifaFinDeSemana: 420,
            tarifaTemporadaAlta: 525,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%'
        },
        {
            tipoHabitacion: 'Suite Presidencial',
            totalHabitaciones: 2,
            tarifaBase: 500,
            tarifaFinDeSemana: 600,
            tarifaTemporadaAlta: 750,
            variacionFinDeSemana: '+20%',
            variacionTemporadaAlta: '+50%'
        }
    ];
}
