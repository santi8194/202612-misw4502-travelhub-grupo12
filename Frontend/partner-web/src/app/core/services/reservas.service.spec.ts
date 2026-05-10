import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ReservasService, ReservaPorPropiedadApi, ReservaDetalleApi, ReservaTimelineApi } from './reservas.service';
import { environment } from '../../../environments/environment';

describe('ReservasService', () => {
    let service: ReservasService;
    let httpMock: HttpTestingController;

    const base = environment.bookingApiUrl;

    const mockReservas: ReservaPorPropiedadApi[] = [
        {
            id_reserva: 'r1',
            id_usuario: 'u1',
            nombre_usuario: 'John Doe',
            id_propiedad: 'p1',
            id_categoria: 'c1',
            habitacion: 'Estándar',
            estado: 'CONFIRMADA',
            fecha_check_in: '2026-03-01',
            fecha_check_out: '2026-03-04',
            huespedes: 2,
            pago: 'APPROVED',
            total: 300,
        },
    ];

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
        paso_actual: 5,
        total_eventos: 5,
        timeline: [
            {
                id_log: 'l1',
                tipo_mensaje: 'EVENTO',
                accion: 'ReservaCreadaIntegracionEvt',
                payload: null,
                fecha_registro: '2026-02-01T10:00:00',
            },
        ],
    };

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                ReservasService,
                provideHttpClient(),
                provideHttpClientTesting(),
            ],
        });
        service = TestBed.inject(ReservasService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    // ─── getReservasPorPropiedad ───

    describe('getReservasPorPropiedad', () => {
        it('should GET reservas for a propiedad', () => {
            service.getReservasPorPropiedad('p1').subscribe((res) => {
                expect(res.length).toBe(1);
                expect(res[0].id_reserva).toBe('r1');
                expect(res[0].nombre_usuario).toBe('John Doe');
            });

            const req = httpMock.expectOne(`${base}/reserva/propiedad/p1`);
            expect(req.request.method).toBe('GET');
            req.flush(mockReservas);
        });

        it('should return an empty array when no reservas exist', () => {
            service.getReservasPorPropiedad('p-empty').subscribe((res) => {
                expect(res).toEqual([]);
            });

            const req = httpMock.expectOne(`${base}/reserva/propiedad/p-empty`);
            req.flush([]);
        });

        it('should URL-encode special characters in propiedad id', () => {
            service.getReservasPorPropiedad('p 1/2').subscribe();

            const req = httpMock.expectOne(`${base}/reserva/propiedad/p%201%2F2`);
            expect(req.request.method).toBe('GET');
            req.flush([]);
        });
    });

    // ─── getReservaPorId ───

    describe('getReservaPorId', () => {
        it('should GET detalle reserva by id', () => {
            service.getReservaPorId('r1').subscribe((res) => {
                expect(res.id_reserva).toBe('r1');
                expect(res.estado).toBe('CONFIRMADA');
                expect(res.ocupacion?.adultos).toBe(2);
            });

            const req = httpMock.expectOne(`${base}/reserva/r1`);
            expect(req.request.method).toBe('GET');
            req.flush(mockDetalle);
        });

        it('should URL-encode the reserva id', () => {
            service.getReservaPorId('r 1').subscribe();

            const req = httpMock.expectOne(`${base}/reserva/r%201`);
            expect(req.request.method).toBe('GET');
            req.flush(mockDetalle);
        });
    });

    // ─── getTimelinePorReserva ───

    describe('getTimelinePorReserva', () => {
        it('should GET timeline for a reserva', () => {
            service.getTimelinePorReserva('r1').subscribe((res) => {
                expect(res.id_reserva).toBe('r1');
                expect(res.estado_global).toBe('COMPLETADO');
                expect(res.timeline.length).toBe(1);
                expect(res.timeline[0].accion).toBe('ReservaCreadaIntegracionEvt');
            });

            const req = httpMock.expectOne(`${base}/reserva/r1/timeline`);
            expect(req.request.method).toBe('GET');
            req.flush(mockTimeline);
        });

        it('should URL-encode the reserva id in timeline request', () => {
            service.getTimelinePorReserva('r 1').subscribe();

            const req = httpMock.expectOne(`${base}/reserva/r%201/timeline`);
            expect(req.request.method).toBe('GET');
            req.flush(mockTimeline);
        });
    });
});
