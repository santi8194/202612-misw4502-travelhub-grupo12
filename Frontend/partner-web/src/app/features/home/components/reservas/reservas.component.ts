import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReservasService, ReservaPorPropiedadApi } from '../../../../core/services/reservas.service';

export interface Reserva {
    id: string;
    propietario: string;
    habitacion: string;
    checkIn: Date;
    checkOut: Date;
    huespedes: number;
    estado: 'Confirmada' | 'Pendiente' | 'Cancelada';
    pago: 'Pago' | 'Reembolso' | 'Pendiente';
    total: number;
}

const PAGE_SIZE = 5;

@Component({
    selector: 'app-reservas',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './reservas.component.html',
    styleUrl: './reservas.component.scss'
})
export class ReservasComponent implements OnChanges {
    @Input() idPropiedad: string | null = null;
    @Output() verDetalleReserva = new EventEmitter<Reserva>();

    busqueda = '';
    filtroFecha = '';
    paginaActual = 1;
    readonly tamanioPagina = PAGE_SIZE;
    loading = false;
    loadError = false;
    reservas: Reserva[] = [];

    constructor(private reservasService: ReservasService) {}

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['idPropiedad']) {
            this.cargarReservas();
        }
    }

    get reservasFiltradas(): Reserva[] {
        const termino = this.busqueda.toLowerCase().trim();
        return this.reservas.filter(r => {
            const coincideTexto = !termino ||
                r.propietario.toLowerCase().includes(termino) ||
                r.id.toLowerCase().includes(termino);
            const coincideFecha = !this.filtroFecha ||
                r.checkIn.toISOString().startsWith(this.filtroFecha) ||
                r.checkOut.toISOString().startsWith(this.filtroFecha);
            return coincideTexto && coincideFecha;
        });
    }

    get totalPaginas(): number {
        return Math.ceil(this.reservasFiltradas.length / this.tamanioPagina);
    }

    get paginas(): number[] {
        return Array.from({ length: this.totalPaginas }, (_, i) => i + 1);
    }

    get reservasPagina(): Reserva[] {
        const inicio = (this.paginaActual - 1) * this.tamanioPagina;
        return this.reservasFiltradas.slice(inicio, inicio + this.tamanioPagina);
    }

    irAPagina(pagina: number): void {
        if (pagina >= 1 && pagina <= this.totalPaginas) {
            this.paginaActual = pagina;
        }
    }

    onBusqueda(): void {
        this.paginaActual = 1;
    }

    private cargarReservas(): void {
        this.paginaActual = 1;
        this.loadError = false;

        if (!this.idPropiedad) {
            this.reservas = [];
            return;
        }

        this.loading = true;
        this.reservasService.getReservasPorPropiedad(this.idPropiedad).subscribe({
            next: (items) => {
                this.reservas = items.map((item) => this.mapReserva(item));
                this.loading = false;
            },
            error: () => {
                this.reservas = [];
                this.loading = false;
                this.loadError = true;
            }
        });
    }

    private mapReserva(item: ReservaPorPropiedadApi): Reserva {
        return {
            id: item.id_reserva,
            propietario: item.id_usuario ?? 'N/A',
            habitacion: item.habitacion ?? 'Categoría sin nombre',
            checkIn: this.parseDate(item.fecha_check_in),
            checkOut: this.parseDate(item.fecha_check_out),
            huespedes: item.huespedes ?? 0,
            estado: this.toEstadoUi(item.estado),
            pago: this.toPagoUi(item.pago),
            total: item.total ?? 0,
        };
    }

    private parseDate(value: string | null): Date {
        if (!value) {
            return new Date();
        }
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? new Date() : parsed;
    }

    private toEstadoUi(value: string | null): 'Confirmada' | 'Pendiente' | 'Cancelada' {
        const estado = (value || '').toUpperCase();
        if (estado === 'CONFIRMADA') {
            return 'Confirmada';
        }
        if (estado === 'CANCELADA' || estado === 'EXPIRADA') {
            return 'Cancelada';
        }
        return 'Pendiente';
    }

    private toPagoUi(value: string | null): 'Pago' | 'Reembolso' | 'Pendiente' {
        const pago = (value || '').toUpperCase();
        if (pago === 'PAGO' || pago === 'PAGADO' || pago === 'PAID') {
            return 'Pago';
        }
        if (pago === 'REEMBOLSO' || pago === 'REEMBOLSADO' || pago === 'REFUND') {
            return 'Reembolso';
        }
        return 'Pendiente';
    }

    verDetalle(reserva: Reserva): void {
        this.verDetalleReserva.emit(reserva);
    }

    estadoClass(estado: string): string {
        switch (estado) {
            case 'Confirmada': return 'badge-confirmada';
            case 'Pendiente':  return 'badge-pendiente';
            case 'Cancelada':  return 'badge-cancelada';
            default:           return '';
        }
    }

    pagoClass(pago: string): string {
        switch (pago) {
            case 'Pago':      return 'badge-pago';
            case 'Reembolso': return 'badge-reembolso';
            case 'Pendiente': return 'badge-pago-pendiente';
            default:          return '';
        }
    }
}
