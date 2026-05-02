import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface EventoLinea {
    titulo: string;
    descripcion: string;
    fecha: Date;
    completado: boolean;
}

export interface DetalleReserva {
    id: string;
    codigo: string;
    // Información del Huésped
    nombreCompleto: string;
    correo: string;
    telefono: string;
    direccion: string;
    // Detalles de Habitación y Estadía
    tipoHabitacion: string;
    numeroHabitacion: string;
    piso: string;
    checkIn: Date;
    checkOut: Date;
    totalNoches: number;
    solicitudesEspeciales: string;
    // Estado
    estado: string;
    pago: string;
    reservadoEl: Date;
    // Desglose de precios
    tarifaPorNoche: number;
    impuestosPorcentaje: number;
    // Información de pago
    metodoPago: string;
    idTransaccion: string;
    pagadoEl: Date;
}

@Component({
    selector: 'app-detalle-reserva',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './detalle-reserva.component.html',
    styleUrl: './detalle-reserva.component.scss'
})
export class DetalleReservaComponent {
    @Input() reservaId: string | null = null;
    @Output() volver = new EventEmitter<void>();

    // Mock data — replace with real service call when API is ready
    readonly reserva: DetalleReserva = {
        id: 'BK-2847',
        codigo: 'BK-2847',
        nombreCompleto: 'John Anderson',
        correo: 'john.anderson@email.com',
        telefono: '+1 (555) 123-4567',
        direccion: '123 Main Street, New York, NY 10001',
        tipoHabitacion: 'Deluxe Queen',
        numeroHabitacion: '#204',
        piso: 'Piso 2',
        checkIn: new Date('2026-03-04'),
        checkOut: new Date('2026-03-07'),
        totalNoches: 3,
        solicitudesEspeciales: 'Check-in temprano solicitado, habitación para no fumadores',
        estado: 'Confirmada',
        pago: 'Pago',
        reservadoEl: new Date('2026-02-14'),
        tarifaPorNoche: 150,
        impuestosPorcentaje: 15,
        metodoPago: 'Tarjeta de Crédito',
        idTransaccion: 'TXN-78945612',
        pagadoEl: new Date('2026-02-14'),
    };

    readonly lineasDeTiempo: EventoLinea[] = [
        { titulo: 'Reserva Creada',          descripcion: 'Reserva iniciada por el huésped',                  fecha: new Date('2026-02-15T10:23:00'), completado: true  },
        { titulo: 'Pago Recibido',           descripcion: 'Pago de $517.5 procesado exitosamente',           fecha: new Date('2026-02-15T10:24:00'), completado: true  },
        { titulo: 'Confirmación Enviada',    descripcion: 'Correo de confirmación enviado al huésped',       fecha: new Date('2026-02-15T10:25:00'), completado: true  },
        { titulo: 'Habitación Asignada',     descripcion: 'Habitación #204 asignada',                        fecha: new Date('2026-02-15T11:00:00'), completado: true  },
        { titulo: 'Recordatorio de Check-In',descripcion: 'Correo pre-llegada enviado',                      fecha: new Date('2026-03-04T09:00:00'), completado: true  },
        { titulo: 'Check-In Programado',     descripcion: 'Se espera que el huésped haga check-in',          fecha: new Date('2026-03-05T15:00:00'), completado: false },
        { titulo: 'Check-Out Programado',    descripcion: 'Se espera que el huésped haga check-out',         fecha: new Date('2026-03-08T11:00:00'), completado: false },
    ];

    get subtotal(): number {
        return this.reserva.tarifaPorNoche * this.reserva.totalNoches;
    }

    get impuestos(): number {
        return +(this.subtotal * this.reserva.impuestosPorcentaje / 100).toFixed(1);
    }

    get total(): number {
        return +(this.subtotal + this.impuestos).toFixed(1);
    }

    volverAReservas(): void {
        this.volver.emit();
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
            default:          return 'badge-pendiente-pago';
        }
    }
}
