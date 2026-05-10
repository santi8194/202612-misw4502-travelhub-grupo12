import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SimpleChange } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';
import { ReservasComponent, Reserva } from './reservas.component';
import { ReservasService, ReservaPorPropiedadApi } from '../../../../core/services/reservas.service';
import { TranslateModule } from '@ngx-translate/core';

describe('ReservasComponent', () => {
    let component: ReservasComponent;
    let fixture: ComponentFixture<ReservasComponent>;
    let reservasService: jasmine.SpyObj<ReservasService>;

    const makeApiItem = (overrides: Partial<ReservaPorPropiedadApi> = {}): ReservaPorPropiedadApi => ({
        id_reserva: 'r1',
        id_usuario: 'u1',
        nombre_usuario: 'John Doe',
        id_propiedad: 'p1',
        id_categoria: 'cat-1',
        habitacion: 'Estándar',
        estado: 'CONFIRMADA',
        fecha_check_in: '2026-03-01',
        fecha_check_out: '2026-03-04',
        huespedes: 2,
        pago: 'APPROVED',
        total: 300,
        ...overrides,
    });

    beforeEach(async () => {
        reservasService = jasmine.createSpyObj('ReservasService', ['getReservasPorPropiedad']);
        reservasService.getReservasPorPropiedad.and.returnValue(of([]));

        await TestBed.configureTestingModule({
            imports: [ReservasComponent, TranslateModule.forRoot()],
            providers: [
                { provide: ReservasService, useValue: reservasService },
                provideHttpClient(),
                provideHttpClientTesting(),
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(ReservasComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    // ─── Creation ───

    it('should create the component', () => {
        expect(component).toBeTruthy();
    });

    it('should start with empty reservas', () => {
        expect(component.reservas).toEqual([]);
    });

    it('should start on page 1', () => {
        expect(component.paginaActual).toBe(1);
    });

    it('should have PAGE_SIZE of 5', () => {
        expect(component.tamanioPagina).toBe(5);
    });

    it('should start with loading false and no error', () => {
        expect(component.loading).toBeFalse();
        expect(component.loadError).toBeFalse();
    });

    // ─── ngOnChanges ───

    it('should NOT call service when idPropiedad is null', () => {
        reservasService.getReservasPorPropiedad.calls.reset();
        component.idPropiedad = null;
        component.ngOnChanges({ idPropiedad: new SimpleChange('p1', null, false) });
        expect(reservasService.getReservasPorPropiedad).not.toHaveBeenCalled();
        expect(component.reservas).toEqual([]);
    });

    it('should call service when idPropiedad is set', () => {
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(reservasService.getReservasPorPropiedad).toHaveBeenCalledWith('p1');
    });

    it('should populate reservas on successful load', () => {
        reservasService.getReservasPorPropiedad.and.returnValue(of([makeApiItem()]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });

        expect(component.reservas.length).toBe(1);
        expect(component.reservas[0].id).toBe('r1');
        expect(component.reservas[0].propietario).toBe('John Doe');
        expect(component.loading).toBeFalse();
        expect(component.loadError).toBeFalse();
    });

    it('should set loadError on service failure', () => {
        reservasService.getReservasPorPropiedad.and.returnValue(throwError(() => new Error('Network error')));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });

        expect(component.reservas).toEqual([]);
        expect(component.loading).toBeFalse();
        expect(component.loadError).toBeTrue();
    });

    it('should reset to page 1 when idPropiedad changes', () => {
        component.paginaActual = 3;
        reservasService.getReservasPorPropiedad.and.returnValue(of([]));
        component.idPropiedad = 'p2';
        component.ngOnChanges({ idPropiedad: new SimpleChange('p1', 'p2', false) });
        expect(component.paginaActual).toBe(1);
    });

    // ─── mapReserva: propietario fallback ───

    it('should use id_usuario if nombre_usuario is null', () => {
        const item = makeApiItem({ nombre_usuario: null, id_usuario: 'u-123' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].propietario).toBe('u-123');
    });

    it('should use N/A when both nombre_usuario and id_usuario are null', () => {
        const item = makeApiItem({ nombre_usuario: null, id_usuario: null });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].propietario).toBe('N/A');
    });

    it('should use habitacion fallback when null', () => {
        const item = makeApiItem({ habitacion: null });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].habitacion).toBe('Categoría sin nombre');
    });

    it('should default total to 0 when null', () => {
        const item = makeApiItem({ total: null });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].total).toBe(0);
    });

    // ─── toEstadoUi ───

    it('should map CONFIRMADA to Confirmada', () => {
        const item = makeApiItem({ estado: 'CONFIRMADA' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].estado).toBe('Confirmada');
    });

    it('should map CANCELADA to Cancelada', () => {
        const item = makeApiItem({ estado: 'CANCELADA' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].estado).toBe('Cancelada');
    });

    it('should map EXPIRADA to Cancelada', () => {
        const item = makeApiItem({ estado: 'EXPIRADA' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].estado).toBe('Cancelada');
    });

    it('should map unknown estado to Pendiente', () => {
        const item = makeApiItem({ estado: 'HOLD' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].estado).toBe('Pendiente');
    });

    it('should map null estado to Pendiente', () => {
        const item = makeApiItem({ estado: null });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].estado).toBe('Pendiente');
    });

    // ─── toPagoUi ───

    it('should map APPROVED to Pago', () => {
        const item = makeApiItem({ pago: 'APPROVED' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Pago');
    });

    it('should map PAGO to Pago', () => {
        const item = makeApiItem({ pago: 'PAGO' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Pago');
    });

    it('should map PAGADO to Pago', () => {
        const item = makeApiItem({ pago: 'PAGADO' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Pago');
    });

    it('should map PAID to Pago', () => {
        const item = makeApiItem({ pago: 'PAID' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Pago');
    });

    it('should map REFUNDED to Reembolso', () => {
        const item = makeApiItem({ pago: 'REFUNDED' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Reembolso');
    });

    it('should map REEMBOLSO to Reembolso', () => {
        const item = makeApiItem({ pago: 'REEMBOLSO' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Reembolso');
    });

    it('should map REEMBOLSADO to Reembolso', () => {
        const item = makeApiItem({ pago: 'REEMBOLSADO' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Reembolso');
    });

    it('should map REFUND to Reembolso', () => {
        const item = makeApiItem({ pago: 'REFUND' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Reembolso');
    });

    it('should map null pago to Pendiente', () => {
        const item = makeApiItem({ pago: null });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Pendiente');
    });

    it('should map unknown pago to Pendiente', () => {
        const item = makeApiItem({ pago: 'DESCONOCIDO' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].pago).toBe('Pendiente');
    });

    // ─── parseDate (via mapReserva) ───

    it('should handle null fecha_check_in', () => {
        const item = makeApiItem({ fecha_check_in: null });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].checkIn).toBeInstanceOf(Date);
    });

    it('should handle invalid date string in fecha_check_out', () => {
        const item = makeApiItem({ fecha_check_out: 'not-a-date' });
        reservasService.getReservasPorPropiedad.and.returnValue(of([item]));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservas[0].checkOut).toBeInstanceOf(Date);
    });

    // ─── Filters ───

    it('reservasFiltradas should return all when no filters', () => {
        const items = [makeApiItem({ id_reserva: 'r1' }), makeApiItem({ id_reserva: 'r2' })];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservasFiltradas.length).toBe(2);
    });

    it('should filter by busqueda matching propietario', () => {
        const items = [
            makeApiItem({ id_reserva: 'r1', nombre_usuario: 'Alice' }),
            makeApiItem({ id_reserva: 'r2', nombre_usuario: 'Bob' }),
        ];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.busqueda = 'ali';
        expect(component.reservasFiltradas.length).toBe(1);
        expect(component.reservasFiltradas[0].propietario).toBe('Alice');
    });

    it('should filter by busqueda matching id', () => {
        const items = [
            makeApiItem({ id_reserva: 'abc-123' }),
            makeApiItem({ id_reserva: 'xyz-456' }),
        ];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.busqueda = 'abc';
        expect(component.reservasFiltradas.length).toBe(1);
    });

    it('should filter by filtroEstado', () => {
        const items = [
            makeApiItem({ id_reserva: 'r1', estado: 'CONFIRMADA' }),
            makeApiItem({ id_reserva: 'r2', estado: 'CANCELADA' }),
        ];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.filtroEstado = 'Confirmada';
        expect(component.reservasFiltradas.length).toBe(1);
        expect(component.reservasFiltradas[0].estado).toBe('Confirmada');
    });

    it('should filter by filtroPago', () => {
        const items = [
            makeApiItem({ id_reserva: 'r1', pago: 'APPROVED' }),
            makeApiItem({ id_reserva: 'r2', pago: 'REFUNDED' }),
        ];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.filtroPago = 'Reembolso';
        expect(component.reservasFiltradas.length).toBe(1);
        expect(component.reservasFiltradas[0].pago).toBe('Reembolso');
    });

    it('should filter by filtroFecha matching checkIn', () => {
        const items = [
            makeApiItem({ id_reserva: 'r1', fecha_check_in: '2026-03-01', fecha_check_out: '2026-03-04' }),
            makeApiItem({ id_reserva: 'r2', fecha_check_in: '2026-04-10', fecha_check_out: '2026-04-15' }),
        ];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.filtroFecha = '2026-03-01';
        expect(component.reservasFiltradas.length).toBe(1);
    });

    it('should filter by filtroFecha matching checkOut', () => {
        const items = [
            makeApiItem({ id_reserva: 'r1', fecha_check_in: '2026-03-01', fecha_check_out: '2026-03-04' }),
            makeApiItem({ id_reserva: 'r2', fecha_check_in: '2026-04-10', fecha_check_out: '2026-04-15' }),
        ];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.filtroFecha = '2026-03-04';
        expect(component.reservasFiltradas.length).toBe(1);
    });

    it('should combine multiple filters', () => {
        const items = [
            makeApiItem({ id_reserva: 'r1', nombre_usuario: 'Alice', estado: 'CONFIRMADA', pago: 'APPROVED' }),
            makeApiItem({ id_reserva: 'r2', nombre_usuario: 'Alice', estado: 'CANCELADA', pago: 'REFUNDED' }),
            makeApiItem({ id_reserva: 'r3', nombre_usuario: 'Bob', estado: 'CONFIRMADA', pago: 'APPROVED' }),
        ];
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.busqueda = 'alice';
        component.filtroEstado = 'Confirmada';
        expect(component.reservasFiltradas.length).toBe(1);
        expect(component.reservasFiltradas[0].id).toBe('r1');
    });

    // ─── Pagination ───

    it('totalPaginas should be 0 with empty list', () => {
        expect(component.totalPaginas).toBe(0);
    });

    it('totalPaginas should be 2 for 6 items', () => {
        const items = Array.from({ length: 6 }, (_, i) => makeApiItem({ id_reserva: `r${i}` }));
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.totalPaginas).toBe(2);
    });

    it('paginas should return array of page numbers', () => {
        const items = Array.from({ length: 6 }, (_, i) => makeApiItem({ id_reserva: `r${i}` }));
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.paginas).toEqual([1, 2]);
    });

    it('reservasPagina should return first 5 items on page 1', () => {
        const items = Array.from({ length: 6 }, (_, i) => makeApiItem({ id_reserva: `r${i}` }));
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        expect(component.reservasPagina.length).toBe(5);
    });

    it('irAPagina should navigate to valid page and return remaining items', () => {
        const items = Array.from({ length: 6 }, (_, i) => makeApiItem({ id_reserva: `r${i}` }));
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.irAPagina(2);
        expect(component.paginaActual).toBe(2);
        expect(component.reservasPagina.length).toBe(1);
    });

    it('irAPagina should not navigate below page 1', () => {
        component.irAPagina(0);
        expect(component.paginaActual).toBe(1);
    });

    it('irAPagina should not navigate beyond last page', () => {
        const items = Array.from({ length: 3 }, (_, i) => makeApiItem({ id_reserva: `r${i}` }));
        reservasService.getReservasPorPropiedad.and.returnValue(of(items));
        component.idPropiedad = 'p1';
        component.ngOnChanges({ idPropiedad: new SimpleChange(null, 'p1', true) });
        component.irAPagina(99);
        expect(component.paginaActual).toBe(1);
    });

    it('onBusqueda should reset to page 1', () => {
        component.paginaActual = 3;
        component.onBusqueda();
        expect(component.paginaActual).toBe(1);
    });

    // ─── verDetalle ───

    it('verDetalle should emit verDetalleReserva event', () => {
        const emitted: Reserva[] = [];
        component.verDetalleReserva.subscribe((r) => emitted.push(r));

        const reserva: Reserva = {
            id: 'r1',
            propietario: 'John',
            habitacion: 'Suite',
            checkIn: new Date(),
            checkOut: new Date(),
            huespedes: 2,
            estado: 'Confirmada',
            pago: 'Pago',
            total: 300,
        };
        component.verDetalle(reserva);
        expect(emitted.length).toBe(1);
        expect(emitted[0].id).toBe('r1');
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
        expect(component.estadoClass('Desconocido')).toBe('');
    });

    // ─── pagoClass ───

    it('pagoClass should return badge-pago for Pago', () => {
        expect(component.pagoClass('Pago')).toBe('badge-pago');
    });

    it('pagoClass should return badge-reembolso for Reembolso', () => {
        expect(component.pagoClass('Reembolso')).toBe('badge-reembolso');
    });

    it('pagoClass should return badge-pago-pendiente for Pendiente', () => {
        expect(component.pagoClass('Pendiente')).toBe('badge-pago-pendiente');
    });

    it('pagoClass should return empty string for unknown', () => {
        expect(component.pagoClass('Desconocido')).toBe('');
    });
});
