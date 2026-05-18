import { Component, HostListener, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { ReservasService, ReservaPorPropiedadApi } from '../../../../core/services/reservas.service';

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
export class ReporteIngresosComponent implements OnChanges {
    @Input() idPropiedad: string | null = null;

    loadingResumen = false;
    resumenError   = false;
    mostrarMenuExport = false;
    filtroDesde = '';
    filtroHasta = '';
    private reservasPropiedad: ReservaPorPropiedadApi[] = [];

    get reservasFiltradas(): ReservaPorPropiedadApi[] {
        if (!this.filtroDesde && !this.filtroHasta) { return this.reservasPropiedad; }
        return this.reservasPropiedad.filter(r => {
            const mes = (r.fecha_check_in ?? '').substring(0, 7);
            if (this.filtroDesde && mes < this.filtroDesde) { return false; }
            if (this.filtroHasta && mes > this.filtroHasta) { return false; }
            return true;
        });
    }

    constructor(private reservasService: ReservasService) {}

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

    get totalIngresosPropiedad(): number {
        return this.reservasFiltradas.reduce((sum, reserva) => sum + (reserva.total ?? 0), 0);
    }

    get totalReservas(): number {
        return this.datosMensuales.reduce((sum, d) => sum + d.reservas, 0);
    }

    get totalReservasPropiedad(): number {
        return this.reservasFiltradas.length;
    }

    get reservasConfirmadasPropiedad(): number {
        return this.reservasFiltradas.filter(r => r.estado === 'CONFIRMADA').length;
    }

    get tasaCancelacionPropiedad(): number {
        if (this.reservasFiltradas.length === 0) { return 0; }
        const canceladas = this.reservasFiltradas.filter(r => r.estado === 'CANCELADA').length;
        return (canceladas / this.reservasFiltradas.length) * 100;
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

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['idPropiedad']) {
            this.cargarResumen();
        }
    }

    private cargarResumen(): void {
        this.resumenError = false;

        if (!this.idPropiedad) {
            this.reservasPropiedad = [];
            this.loadingResumen = false;
            return;
        }

        this.loadingResumen = true;
        this.reservasService.getReservasPorPropiedad(this.idPropiedad).subscribe({
            next: (reservas) => {
                this.reservasPropiedad = reservas;
                this.loadingResumen = false;
            },
            error: () => {
                this.reservasPropiedad = [];
                this.loadingResumen = false;
                this.resumenError = true;
            }
        });
    }

    // ─── SVG line chart helpers ───────────────────────────────────────────────

    readonly chartWidth  = 560;
    readonly chartHeight = 160;
    readonly chartPadX   = 10;
    readonly chartPadY   = 10;

    get ingresosMensualesPropiedad(): number[] {
        const monthly = new Array(12).fill(0);
        for (const r of this.reservasFiltradas) {
            if (r.fecha_check_in && r.total) {
                const mes = new Date(r.fecha_check_in).getMonth();
                monthly[mes] += r.total;
            }
        }
        return monthly;
    }

    get maxIngresoPropiedad(): number {
        const max = Math.max(...this.ingresosMensualesPropiedad);
        return max > 0 ? max : 1;
    }

    get linePoints(): string {
        const data = this.ingresosMensualesPropiedad;
        const max  = this.maxIngresoPropiedad;
        return data.map((val, i) => {
            const x = this.chartPadX + (i / (data.length - 1)) * (this.chartWidth - 2 * this.chartPadX);
            const y = this.chartHeight - this.chartPadY - ((val / max) * (this.chartHeight - 2 * this.chartPadY));
            return `${x},${y}`;
        }).join(' ');
    }

    get areaPath(): string {
        const data = this.ingresosMensualesPropiedad;
        const max  = this.maxIngresoPropiedad;
        const pts  = data.map((val, i) => {
            const x = this.chartPadX + (i / (data.length - 1)) * (this.chartWidth - 2 * this.chartPadX);
            const y = this.chartHeight - this.chartPadY - ((val / max) * (this.chartHeight - 2 * this.chartPadY));
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

    get reservasMensualesPropiedad(): number[] {
        const monthly = new Array(12).fill(0);
        for (const r of this.reservasFiltradas) {
            if (r.fecha_check_in) {
                const mes = new Date(r.fecha_check_in).getMonth();
                monthly[mes]++;
            }
        }
        return monthly;
    }

    get confirmadasMensualesPropiedad(): number[] {
        const monthly = new Array(12).fill(0);
        for (const r of this.reservasFiltradas) {
            if (r.fecha_check_in && r.estado === 'CONFIRMADA') {
                const mes = new Date(r.fecha_check_in).getMonth();
                monthly[mes]++;
            }
        }
        return monthly;
    }

    get canceladasMensualesPropiedad(): number[] {
        const monthly = new Array(12).fill(0);
        for (const r of this.reservasFiltradas) {
            if (r.fecha_check_in && r.estado === 'CANCELADA') {
                const mes = new Date(r.fecha_check_in).getMonth();
                monthly[mes]++;
            }
        }
        return monthly;
    }

    get huespedesMensualesPropiedad(): number[] {
        const monthly = new Array(12).fill(0);
        for (const r of this.reservasFiltradas) {
            if (r.fecha_check_in) {
                const mes = new Date(r.fecha_check_in).getMonth();
                monthly[mes] += r.huespedes ?? 0;
            }
        }
        return monthly;
    }

    get totalCanceladasPropiedad(): number {
        return this.reservasFiltradas.filter(r => r.estado === 'CANCELADA').length;
    }

    get totalHuespedesPropiedad(): number {
        return this.reservasFiltradas.reduce((sum, r) => sum + (r.huespedes ?? 0), 0);
    }

    get barIndices(): number[] {
        return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
    }

    get maxReservas(): number {
        const max = Math.max(...this.reservasMensualesPropiedad);
        return max > 0 ? max : 1;
    }

    getBarX(index: number, isSecond: boolean): number {
        const usable = this.barChartWidth - 2 * this.barChartPadX;
        const step = usable / 12;
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


    exportarReporte(): void {
        // Legacy CSV kept for test compatibility
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

    toggleMenuExport(event: MouseEvent): void {
        event.stopPropagation();
        this.mostrarMenuExport = !this.mostrarMenuExport;
    }

    @HostListener('document:click')
    cerrarMenuExport(): void {
        this.mostrarMenuExport = false;
    }

    private readonly nombresMeses = [
        'Enero','Febrero','Marzo','Abril','Mayo','Junio',
        'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'
    ];

    exportarPdf(): void {
        this.mostrarMenuExport = false;
        const doc  = new jsPDF();
        const hoy  = new Date().toLocaleDateString('es-CO');

        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text('Reporte de Ingresos', 14, 20);
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text(`Generado: ${hoy}`, 14, 28);

        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Resumen General', 14, 40);

        autoTable(doc, {
            startY: 44,
            head: [['Indicador', 'Valor']],
            body: [
                ['Ingresos Totales',      `$${this.totalIngresosPropiedad.toLocaleString('es-CO')}`],
                ['Total Reservas',        this.totalReservasPropiedad.toString()],
                ['Reservas Confirmadas',  this.reservasConfirmadasPropiedad.toString()],
                ['Tasa de Cancelaci\u00f3n', `${this.tasaCancelacionPropiedad.toFixed(1)}%`],
            ],
            theme: 'grid',
            headStyles: { fillColor: [30, 58, 95] },
            styles: { fontSize: 10 }
        });

        const afterKpi = (doc as any).lastAutoTable.finalY + 10;
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Detalle Mensual', 14, afterKpi);

        const ing  = this.ingresosMensualesPropiedad;
        const res  = this.reservasMensualesPropiedad;
        const con  = this.confirmadasMensualesPropiedad;
        const can  = this.canceladasMensualesPropiedad;
        const hues = this.huespedesMensualesPropiedad;

        autoTable(doc, {
            startY: afterKpi + 4,
            head: [['Mes', 'Ingresos', 'Reservas', 'Confirmadas', 'Canceladas', 'Hu\u00e9spedes']],
            body: this.nombresMeses.map((mes, i) => [
                mes,
                `$${ing[i].toLocaleString('es-CO')}`,
                res[i], con[i], can[i], hues[i]
            ]),
            foot: [[
                'TOTAL',
                `$${this.totalIngresosPropiedad.toLocaleString('es-CO')}`,
                this.totalReservasPropiedad,
                this.reservasConfirmadasPropiedad,
                this.totalCanceladasPropiedad,
                this.totalHuespedesPropiedad
            ]],
            theme: 'striped',
            headStyles: { fillColor: [30, 58, 95] },
            footStyles: { fillColor: [220, 220, 220], fontStyle: 'bold', textColor: [0, 0, 0] },
            styles: { fontSize: 9 }
        });

        doc.save(`reporte-ingresos-${hoy.replace(/\//g, '-')}.pdf`);
    }

    exportarExcel(): void {
        this.mostrarMenuExport = false;
        const ing  = this.ingresosMensualesPropiedad;
        const res  = this.reservasMensualesPropiedad;
        const con  = this.confirmadasMensualesPropiedad;
        const can  = this.canceladasMensualesPropiedad;
        const hues = this.huespedesMensualesPropiedad;

        const resumenData = [
            ['Mes', 'Ingresos Totales', 'Reservas', 'Confirmadas', 'Canceladas', 'Hu\u00e9spedes'],
            ...this.nombresMeses.map((mes, i) => [mes, ing[i], res[i], con[i], can[i], hues[i]]),
            ['TOTAL', this.totalIngresosPropiedad, this.totalReservasPropiedad,
             this.reservasConfirmadasPropiedad, this.totalCanceladasPropiedad, this.totalHuespedesPropiedad]
        ];

        const reservasData = [
            ['ID Reserva', 'Hu\u00e9sped', 'Estado', 'Check-in', 'Check-out', 'Hu\u00e9spedes', 'Total'],
            ...this.reservasPropiedad.map(r => [
                r.id_reserva, r.nombre_usuario, r.estado,
                r.fecha_check_in, r.fecha_check_out, r.huespedes, r.total ?? 0
            ])
        ];

        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(resumenData), 'Resumen Mensual');
        XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(reservasData), 'Reservas');

        const hoy = new Date().toLocaleDateString('es-CO').replace(/\//g, '-');
        XLSX.writeFile(wb, `reporte-ingresos-${hoy}.xlsx`);
    }
}
