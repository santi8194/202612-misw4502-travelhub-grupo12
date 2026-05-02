import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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

const MOCK_RESERVAS: Reserva[] = [
    { id: 'BK001', propietario: 'John Smith',      habitacion: 'Suite Deluxe',        checkIn: new Date('2026-03-14'), checkOut: new Date('2026-03-17'), huespedes: 2, estado: 'Confirmada', pago: 'Pago',      total: 450  },
    { id: 'BK002', propietario: 'Sarah Johnson',   habitacion: 'Habitación Estándar', checkIn: new Date('2026-03-16'), checkOut: new Date('2026-03-20'), huespedes: 1, estado: 'Confirmada', pago: 'Pago',      total: 320  },
    { id: 'BK003', propietario: 'Michael Brown',   habitacion: 'Suite Ejecutiva',     checkIn: new Date('2026-03-19'), checkOut: new Date('2026-03-24'), huespedes: 3, estado: 'Pendiente',  pago: 'Pago',      total: 750  },
    { id: 'BK004', propietario: 'Emily Davis',     habitacion: 'Suite Presidencial',  checkIn: new Date('2026-03-22'), checkOut: new Date('2026-03-28'), huespedes: 2, estado: 'Pendiente',  pago: 'Pendiente', total: 1800 },
    { id: 'BK005', propietario: 'James Miller',    habitacion: 'Suite Deluxe',        checkIn: new Date('2026-03-24'), checkOut: new Date('2026-03-29'), huespedes: 2, estado: 'Cancelada',  pago: 'Reembolso', total: 600  },
    { id: 'BK006', propietario: 'Lisa Anderson',   habitacion: 'Habitación Estándar', checkIn: new Date('2026-03-07'), checkOut: new Date('2026-03-09'), huespedes: 2, estado: 'Pendiente',  pago: 'Pago',      total: 220  },
    { id: 'BK007', propietario: 'Robert Chen',     habitacion: 'Suite Presidencial',  checkIn: new Date('2026-03-21'), checkOut: new Date('2026-03-26'), huespedes: 4, estado: 'Pendiente',  pago: 'Pago',      total: 2500 },
    { id: 'BK008', propietario: 'Maria Garcia',    habitacion: 'Suite Ejecutiva',     checkIn: new Date('2026-04-01'), checkOut: new Date('2026-04-05'), huespedes: 2, estado: 'Confirmada', pago: 'Pago',      total: 900  },
    { id: 'BK009', propietario: 'David Wilson',    habitacion: 'Habitación Estándar', checkIn: new Date('2026-04-03'), checkOut: new Date('2026-04-07'), huespedes: 1, estado: 'Pendiente',  pago: 'Pendiente', total: 360  },
    { id: 'BK010', propietario: 'Anna Martinez',   habitacion: 'Suite Deluxe',        checkIn: new Date('2026-04-10'), checkOut: new Date('2026-04-14'), huespedes: 3, estado: 'Confirmada', pago: 'Pago',      total: 680  },
];

const PAGE_SIZE = 5;

@Component({
    selector: 'app-reservas',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './reservas.component.html',
    styleUrl: './reservas.component.scss'
})
export class ReservasComponent {
    busqueda = '';
    filtroFecha = '';
    paginaActual = 1;
    readonly tamanioPagina = PAGE_SIZE;

    get reservasFiltradas(): Reserva[] {
        const termino = this.busqueda.toLowerCase().trim();
        return MOCK_RESERVAS.filter(r => {
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

    verDetalle(reserva: Reserva): void {
        console.log('Ver detalle:', reserva.id);
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
