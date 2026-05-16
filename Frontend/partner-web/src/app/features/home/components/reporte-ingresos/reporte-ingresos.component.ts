import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

export interface FilaReporteMensual {
    mes: string;
    ingresosTotales: number;
    habitaciones: number;
    servicios: number;
    impuestos: number;
    reservas: number;
}

export interface PuntoGrafico {
    label: string;
    valor: number;
    reservas: number;
    ocupacion: number;
}

@Component({
    selector: 'app-reporte-ingresos',
    standalone: true,
    imports: [CommonModule, TranslateModule],
    templateUrl: './reporte-ingresos.component.html',
    styleUrl: './reporte-ingresos.component.scss'
})
export class ReporteIngresosComponent {

    readonly datosMensuales: FilaReporteMensual[] = [
        { mes: 'REPORTS.MONTHS.JAN', ingresosTotales: 65000,    habitaciones: 55250,  servicios: 6500,  impuestos: 3250,  reservas: 180 },
        { mes: 'REPORTS.MONTHS.FEB', ingresosTotales: 72000,    habitaciones: 61200,  servicios: 7200,  impuestos: 3600,  reservas: 195 },
        { mes: 'REPORTS.MONTHS.MAR', ingresosTotales: 85000,    habitaciones: 72250,  servicios: 8500,  impuestos: 4250,  reservas: 210 },
        { mes: 'REPORTS.MONTHS.APR', ingresosTotales: 95000,    habitaciones: 80750,  servicios: 9500,  impuestos: 4750,  reservas: 245 },
        { mes: 'REPORTS.MONTHS.MAY', ingresosTotales: 110000,   habitaciones: 93500,  servicios: 11000, impuestos: 5500,  reservas: 270 },
        { mes: 'REPORTS.MONTHS.JUN', ingresosTotales: 127485,   habitaciones: 108362, servicios: 12748, impuestos: 6374,  reservas: 290 },
        { mes: 'REPORTS.MONTHS.JUL', ingresosTotales: 145000,   habitaciones: 123250, servicios: 14500, impuestos: 7250,  reservas: 330 },
        { mes: 'REPORTS.MONTHS.AUG', ingresosTotales: 152000,   habitaciones: 129200, servicios: 15200, impuestos: 7600,  reservas: 345 },
        { mes: 'REPORTS.MONTHS.SEP', ingresosTotales: 118000,   habitaciones: 100300, servicios: 11800, impuestos: 5900,  reservas: 255 },
        { mes: 'REPORTS.MONTHS.OCT', ingresosTotales: 105000,   habitaciones: 89250,  servicios: 10500, impuestos: 5250,  reservas: 240 },
        { mes: 'REPORTS.MONTHS.NOV', ingresosTotales: 92000,    habitaciones: 78200,  servicios: 9200,  impuestos: 4600,  reservas: 230 },
        { mes: 'REPORTS.MONTHS.DEC', ingresosTotales: 135000,   habitaciones: 114750, servicios: 13500, impuestos: 6750,  reservas: 305 },
    ];

    get totalAnual(): number {
        return this.datosMensuales.reduce((sum, d) => sum + d.ingresosTotales, 0);
    }

    get totalReservas(): number {
        return this.datosMensuales.reduce((sum, d) => sum + d.reservas, 0);
    }

    get totalHabitaciones(): number {
        return this.datosMensuales.reduce((sum, d) => sum + d.habitaciones, 0);
    }

    get totalServicios(): number {
        return this.datosMensuales.reduce((sum, d) => sum + d.servicios, 0);
    }

    get totalImpuestos(): number {
        return this.datosMensuales.reduce((sum, d) => sum + d.impuestos, 0);
    }

    // ─── SVG line chart helpers ───────────────────────────────────────────────

    readonly chartWidth  = 560;
    readonly chartHeight = 160;
    readonly chartPadX   = 10;
    readonly chartPadY   = 10;

    private get maxIngreso(): number {
        return Math.max(...this.datosMensuales.map(d => d.ingresosTotales));
    }

    get linePoints(): string {
        return this.datosMensuales.map((d, i) => {
            const x = this.chartPadX + (i / (this.datosMensuales.length - 1)) * (this.chartWidth - 2 * this.chartPadX);
            const y = this.chartHeight - this.chartPadY - ((d.ingresosTotales / this.maxIngreso) * (this.chartHeight - 2 * this.chartPadY));
            return `${x},${y}`;
        }).join(' ');
    }

    get areaPath(): string {
        const pts = this.datosMensuales.map((d, i) => {
            const x = this.chartPadX + (i / (this.datosMensuales.length - 1)) * (this.chartWidth - 2 * this.chartPadX);
            const y = this.chartHeight - this.chartPadY - ((d.ingresosTotales / this.maxIngreso) * (this.chartHeight - 2 * this.chartPadY));
            return `${x},${y}`;
        });
        const first = pts[0];
        const last  = pts[pts.length - 1];
        const bottomRight = `${last.split(',')[0]},${this.chartHeight - this.chartPadY}`;
        const bottomLeft  = `${first.split(',')[0]},${this.chartHeight - this.chartPadY}`;
        return `M ${first} L ${pts.slice(1).join(' L ')} L ${bottomRight} L ${bottomLeft} Z`;
    }

    get lineChartLabels(): string[] {
        return ['REPORTS.MONTHS.JAN','REPORTS.MONTHS.FEB','REPORTS.MONTHS.MAR',
                'REPORTS.MONTHS.APR','REPORTS.MONTHS.MAY','REPORTS.MONTHS.JUN',
                'REPORTS.MONTHS.JUL','REPORTS.MONTHS.AUG','REPORTS.MONTHS.SEP',
                'REPORTS.MONTHS.OCT','REPORTS.MONTHS.NOV','REPORTS.MONTHS.DEC'];
    }

    // ─── Bar chart helpers ────────────────────────────────────────────────────

    readonly barChartHeight = 200;
    readonly barChartPadX   = 30;
    readonly barChartPadY   = 16;
    readonly barWidth       = 14;
    readonly barGap         = 6;
    readonly groupGap       = 18;
    readonly barChartWidth  = 560;

    get maxReservas(): number {
        return Math.max(...this.datosMensuales.map(d => d.reservas));
    }

    get maxOcupacion(): number { return 100; }

    getBarX(index: number, isSecond: boolean): number {
        const groupWidth = this.barWidth * 2 + this.barGap + this.groupGap;
        const usable = this.barChartWidth - 2 * this.barChartPadX;
        const totalGroups = this.datosMensuales.length;
        const step = usable / totalGroups;
        const groupStart = this.barChartPadX + index * step + (step - (this.barWidth * 2 + this.barGap)) / 2;
        return isSecond ? groupStart + this.barWidth + this.barGap : groupStart;
    }

    getBarHeight(value: number, max: number): number {
        const usable = this.barChartHeight - 2 * this.barChartPadY;
        return (value / max) * usable;
    }

    getBarY(value: number, max: number): number {
        return this.barChartHeight - this.barChartPadY - this.getBarHeight(value, max);
    }

    getOcupacion(mes: FilaReporteMensual): number {
        // Simulated occupancy derived from reservas ratio
        return Math.min(100, Math.round((mes.reservas / 365) * 100 * 3));
    }

    exportarReporte(): void {
        // Mock export — in production this would trigger a PDF/CSV download
        const csvLines = [
            ['Mes', 'Ingresos Totales', 'Habitaciones', 'Servicios', 'Impuestos', 'Reservas'].join(','),
            ...this.datosMensuales.map(d =>
                [d.mes, d.ingresosTotales, d.habitaciones, d.servicios, d.impuestos, d.reservas].join(',')
            ),
            ['TOTAL', this.totalAnual, this.totalHabitaciones, this.totalServicios, this.totalImpuestos, this.totalReservas].join(',')
        ];
        const blob = new Blob([csvLines.join('\n')], { type: 'text/csv;charset=utf-8;' });
        const url  = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href     = url;
        link.download = 'reporte-ingresos.csv';
        link.click();
        URL.revokeObjectURL(url);
    }
}
