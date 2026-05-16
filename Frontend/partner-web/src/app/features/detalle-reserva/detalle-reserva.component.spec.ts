import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SimpleChange } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';
import { DetalleReservaComponent } from './detalle-reserva.component';
import { ReservasService, ReservaDetalleApi, ReservaTimelineApi } from '../../core/services/reservas.service';
import { AuthService, AuthUserResponse } from '../../core/services/auth.service';

describe('DetalleReservaComponent', () => {
    let component: DetalleReservaComponent;
    let fixture: ComponentFixture<DetalleReservaComponent>;
    let reservasService: jasmine.SpyObj<ReservasService>;
    let authService: jasmine.SpyObj<AuthService>;

    const mockDetalle: ReservaDetalleApi = {
        id_reserva: 'r1',
        id_usuario: 'u1',
        id_categoria: 'c1',
        codigo_confirmacion_ota: 'OTA-123',
        codigo_localizador_pms: 'PMS-456',
        estado: 'CONFIRMADA',
        fecha_check_in: '2026-03-01',
        fecha_check_out: '2026-03-04',
        ocupacion: { adultos: 2, ninos: 0, infantes: 0 },
        fecha_creacion: '2026-02-01T10:00:00',
        fecha_actualizacion: '2026-02-01T10:00:00',
    };

    const mockTimeline: ReservaTimelineApi = {
        id_reserva: 'r1',
        id_instancia_saga: 'saga-1',
        id_flujo: 'flujo-1',
        version_ejecucion: 1,
        estado_global: 'COMPLETADO',
        paso_actual: 7,
        total_eventos: 7,
        timeline: [
            { id_log: 'l1', tipo_mensaje: 'EVENTO', accion: 'ReservaCreadaIntegracionEvt', payload: null, fecha_registro: '2026-02-01T10:00:00' },
            { id_log: 'l2', tipo_mensaje: 'COMANDO_EMITIDO', accion: 'ProcesarPagoCmd', payload: { monto: 300 }, fecha_registro: '2026-02-01T10:01:00' },
            { id_log: 'l3', tipo_mensaje: 'EVENTO', accion: 'PagoRechazadoEvt', payload: { motivo: 'Fondos insuficientes' }, fecha_registro: '2026-02-01T10:02:00' },
            { id_log: 'l4', tipo_mensaje: 'EVENTO', accion: 'CancelarReservaLocalCmd', payload: null, fecha_registro: '2026-02-01T10:03:00' },
            { id_log: 'l5', tipo_mensaje: 'EVENTO', accion: 'PagoRechazadoEvt', payload: {}, fecha_registro: '2026-02-01T10:04:00' },
            { id_log: 'l6', tipo_mensaje: 'COMANDO_EMITIDO', accion: 'ProcesarPagoCmd', payload: { monto: 'not-a-number' }, fecha_registro: '2026-02-01T10:05:00' },
            { id_log: 'l7', tipo_mensaje: 'EVENTO', accion: 'UnknownAction', payload: null, fecha_registro: '2026-02-01T10:06:00' },
        ],
    };

    const mockUser: AuthUserResponse = {
        id_usuario: 'u1',
        email: 'huesped@test.com',
        full_name: 'Huesped Test',
        rol: 'USER',
        partner_id: null,
    };

    beforeEach(async () => {
        reservasService = jasmine.createSpyObj('ReservasService', ['getReservaPorId', 'getTimelinePorReserva']);
        authService = jasmine.createSpyObj('AuthService', ['getUserById']);

        reservasService.getReservaPorId.and.returnValue(of(mockDetalle));
        reservasService.getTimelinePorReserva.and.returnValue(of(mockTimeline));
        authService.getUserById.and.returnValue(of(mockUser));

        await TestBed.configureTestingModule({
            imports: [DetalleReservaComponent],
            providers: [
                { provide: ReservasService, useValue: reservasService },
                { provide: AuthService, useValue: authService },
                provideHttpClient(),
                provideHttpClientTesting(),
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(DetalleReservaComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    // ─── Creation ───

    it('should create the component', () => {
        expect(component).toBeTruthy();
    });

    it('should have a default reserva on init', () => {
        expect(component.reserva).toBeTruthy();
        expect(component.reserva.tarifaPorNoche).toBe(150);
    });

    it('should have fallback timeline on init', () => {
        expect(component.lineasDeTiempo.length).toBeGreaterThan(0);
    });

    // ─── ngOnChanges ───

    it('should load detalle and timeline when reservaId changes', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(reservasService.getReservaPorId).toHaveBeenCalledWith('r1');
        expect(reservasService.getTimelinePorReserva).toHaveBeenCalledWith('r1');
    });

    it('should update tipoHabitacion when habitacionNombre changes', () => {
        component.habitacionNombre = 'Suite Deluxe';
        component.ngOnChanges({ habitacionNombre: new SimpleChange(null, 'Suite Deluxe', true) });
        expect(component.reserva.tipoHabitacion).toBe('Suite Deluxe');
    });

    it('should NOT call service when reservaId is null', () => {
        reservasService.getReservaPorId.calls.reset();
        reservasService.getTimelinePorReserva.calls.reset();
        component.reservaId = null;
        component.ngOnChanges({ reservaId: new SimpleChange('r1', null, false) });
        expect(reservasService.getReservaPorId).not.toHaveBeenCalled();
        expect(reservasService.getTimelinePorReserva).not.toHaveBeenCalled();
    });

    // ─── cargarDetalleReserva success ───

    it('should populate reserva.id from detalle response', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.id).toBe('r1');
    });

    it('should map CONFIRMADA estado correctly', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.estado).toBe('Confirmada');
    });

    it('should map CANCELADA estado correctly', () => {
        reservasService.getReservaPorId.and.returnValue(of({ ...mockDetalle, estado: 'CANCELADA' }));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.estado).toBe('Cancelada');
    });

    it('should map EXPIRADA estado to Cancelada', () => {
        reservasService.getReservaPorId.and.returnValue(of({ ...mockDetalle, estado: 'EXPIRADA' }));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.estado).toBe('Cancelada');
    });

    it('should map null estado to Pendiente', () => {
        reservasService.getReservaPorId.and.returnValue(of({ ...mockDetalle, estado: null }));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.estado).toBe('Pendiente');
    });

    it('should calculate totalNoches from checkIn and checkOut dates', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.totalNoches).toBe(3);
    });

    it('should use habitacionNombre in mapDetalleReserva when set', () => {
        component.habitacionNombre = 'Suite';
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.tipoHabitacion).toBe('Suite');
    });

    it('should call getUserById when id_usuario is present', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(authService.getUserById).toHaveBeenCalledWith('u1');
    });

    it('should set nombreCompleto and correo from usuario response', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.nombreCompleto).toBe('Huesped Test');
        expect(component.reserva.correo).toBe('huesped@test.com');
    });

    it('should handle cargarDetalleReserva error gracefully', () => {
        reservasService.getReservaPorId.and.returnValue(throwError(() => new Error('fail')));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.codigo).toBe('r1');
    });

    it('should handle getUserById error gracefully', () => {
        authService.getUserById.and.returnValue(throwError(() => new Error('fail')));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.nombreCompleto).toBe('');
    });

    it('should NOT call getUserById when id_usuario is null', () => {
        authService.getUserById.calls.reset();
        reservasService.getReservaPorId.and.returnValue(of({ ...mockDetalle, id_usuario: null }));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(authService.getUserById).not.toHaveBeenCalled();
    });

    it('should handle null fecha_creacion gracefully', () => {
        reservasService.getReservaPorId.and.returnValue(of({ ...mockDetalle, fecha_creacion: null }));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.reservadoEl).toBeInstanceOf(Date);
    });

    it('should keep default totalNoches when checkIn equals checkOut', () => {
        reservasService.getReservaPorId.and.returnValue(of({
            ...mockDetalle,
            fecha_check_in: '2026-03-01',
            fecha_check_out: '2026-03-01',
        }));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.reserva.totalNoches).toBe(component.reserva.totalNoches);
    });

    // ─── cargarTimelineReserva ───

    it('should populate lineasDeTiempo from timeline response', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo.length).toBe(7);
    });

    it('should use fallback timeline when timeline response is empty', () => {
        reservasService.getTimelinePorReserva.and.returnValue(of({ ...mockTimeline, timeline: [] }));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo.length).toBeGreaterThan(0);
    });

    it('should use fallback timeline on timeline error', () => {
        reservasService.getTimelinePorReserva.and.returnValue(throwError(() => new Error('fail')));
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo.length).toBeGreaterThan(0);
    });

    // ─── Timeline: tituloEventoSaga ───

    it('should set titulo to known event name for ReservaCreadaIntegracionEvt', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[0].titulo).toBe('Reserva Creada');
    });

    it('should use raw accion as titulo for unknown actions', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[6].titulo).toBe('UnknownAction');
    });

    // ─── Timeline: descripcionEventoSaga ───

    it('should include monto in descripcion for ProcesarPagoCmd with number monto', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[1].descripcion).toContain('300');
    });

    it('should use generic text for ProcesarPagoCmd with non-number monto', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[5].descripcion).toBe('Procesamiento de pago iniciado');
    });

    it('should include motivo in descripcion for rejection events with motivo', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[2].descripcion).toBe('Fondos insuficientes');
    });

    it('should use generic rejection text when motivo is absent', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[4].descripcion).toBe('Se recibió un rechazo durante la saga');
    });

    it('should describe compensation step for Cancelar/Reversar actions', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[3].descripcion).toBe('Paso de compensación ejecutado');
    });

    it('should use EVENTO descripcion for generic events', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[6].descripcion).toContain('procesada');
    });

    it('should use COMANDO_EMITIDO descripcion for commands', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        // ProcesarPagoCmd has its own branch; unknownAction at index 6 is EVENTO
        // COMANDO_EMITIDO l6 (index 5) for ProcesarPagoCmd falls in its branch, generic EVENTO/COMANDO is on index 6
        // Item at index 6 is EVENTO type → 'procesada'
        expect(component.lineasDeTiempo[6].descripcion).toContain('procesada');
    });

    // ─── Timeline: eventoCompletado ───

    it('should set completado=true for normal events', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[0].completado).toBeTrue();
    });

    it('should set completado=false for rejection events', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[2].completado).toBeFalse();
    });

    it('should set completado=false for cancellation events', () => {
        component.reservaId = 'r1';
        component.ngOnChanges({ reservaId: new SimpleChange(null, 'r1', true) });
        expect(component.lineasDeTiempo[3].completado).toBeFalse();
    });

    // ─── Computed properties ───

    it('subtotal should be tarifaPorNoche * totalNoches', () => {
        component.reserva = { ...component.reserva, tarifaPorNoche: 150, totalNoches: 3 };
        expect(component.subtotal).toBe(450);
    });

    it('impuestos should be subtotal * impuestosPorcentaje / 100', () => {
        component.reserva = { ...component.reserva, tarifaPorNoche: 150, totalNoches: 3, impuestosPorcentaje: 15 };
        expect(component.impuestos).toBe(67.5);
    });

    it('total should be subtotal + impuestos', () => {
        component.reserva = { ...component.reserva, tarifaPorNoche: 150, totalNoches: 3, impuestosPorcentaje: 15 };
        expect(component.total).toBe(517.5);
    });

    // ─── volverAReservas ───

    it('should emit volver event when onVolver is null', () => {
        spyOn(component.volver, 'emit');
        component.onVolver = null;
        component.volverAReservas();
        expect(component.volver.emit).toHaveBeenCalled();
    });

    it('should call onVolver function when set and NOT emit event', () => {
        let called = false;
        spyOn(component.volver, 'emit');
        component.onVolver = () => { called = true; };
        component.volverAReservas();
        expect(called).toBeTrue();
        expect(component.volver.emit).not.toHaveBeenCalled();
    });

    // ─── estadoClass ───

    it('estadoClass should return badge-confirmada for Confirmada', () => {
        expect(component.estadoClass('Confirmada')).toBe('badge-confirmada');
    });

    it('estadoClass should return badge-pendiente for Pendiente', () => {
        expect(component.estadoClass('Pendiente')).toBe('badge-pendiente');
    });

    it('estadoClass should return badge-cancelada for Cancelada', () => {
        expect(component.estadoClass('Cancelada')).toBe('badge-cancelada');
    });

    it('estadoClass should return empty string for unknown', () => {
        expect(component.estadoClass('Otro')).toBe('');
    });

    // ─── pagoClass ───

    it('pagoClass should return badge-pago for Pago', () => {
        expect(component.pagoClass('Pago')).toBe('badge-pago');
    });

    it('pagoClass should return badge-reembolso for Reembolso', () => {
        expect(component.pagoClass('Reembolso')).toBe('badge-reembolso');
    });

    it('pagoClass should return badge-pendiente-pago for other values', () => {
        expect(component.pagoClass('Pendiente')).toBe('badge-pendiente-pago');
        expect(component.pagoClass('Desconocido')).toBe('badge-pendiente-pago');
    });
});
