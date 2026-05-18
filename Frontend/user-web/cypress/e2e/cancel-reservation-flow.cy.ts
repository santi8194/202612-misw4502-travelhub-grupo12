const RESERVATION_ID = 'res-001';
const USER_ID = 'cc912e74-927e-4166-802b-3ba6a3615ebf';
const CATEGORY_ID = 'cat-001';

function seedAuthSession(window: Window) {
  window.localStorage.setItem('th_access_token', 'fake-access-token');
  window.localStorage.setItem('th_refresh_token', 'fake-refresh-token');
  window.localStorage.setItem('th_token_type', 'Bearer');
  window.localStorage.setItem('th_user_email', 'traveler@example.com');
  window.localStorage.setItem('th_user_id', 'user-123');
  window.localStorage.setItem('th_user_name', 'Traveler');
}

function preview(overrides: Record<string, unknown> = {}) {
  return {
    reservationId: RESERVATION_ID,
    reservationNumber: 'BKUTQOPB5C',
    hotelName: 'Hotel Central',
    location: 'Bogota, Colombia',
    checkInDate: '2026-06-10',
    checkOutDate: '2026-06-13',
    guests: 2,
    currentStatus: 'CONFIRMADA',
    totalPaid: 580,
    currency: 'USD',
    canCancel: true,
    nonCancelableReason: null,
    pmsStatus: 'CONFIRMED',
    mensaje: null,
    cancellationPolicy: {
      type: 'PARTIAL_REFUND',
      label: 'Reembolso parcial',
      description: 'Se aplica una penalidad del 50%.',
      diasAnticipacion: 3,
      porcentajePenalidad: 50,
    },
    refund: {
      paidAmount: 580,
      expectedRefundAmount: 290,
      refundStatus: 'PENDING',
      processingTimeLabel: '5 a 10 dias habiles',
    },
    ...overrides,
  };
}

describe('Cancel Reservation Flow', () => {
  it('navigates from reservation detail to the cancellation page and keeps the reservation', () => {
    cy.intercept('GET', `**/reserva/${RESERVATION_ID}`, {
      id_reserva: RESERVATION_ID,
      id_usuario: USER_ID,
      id_categoria: CATEGORY_ID,
      estado: 'CONFIRMADA',
      fecha_check_in: '2099-06-10',
      fecha_check_out: '2099-06-13',
      fecha_creacion: '2026-01-01T00:00:00Z',
      fecha_actualizacion: '2026-01-01T00:00:00Z',
      codigo_confirmacion_ota: 'TH-001',
      codigo_localizador_pms: null,
      ocupacion: { adultos: 2, ninos: 0, infantes: 0 },
    }).as('getReservationDetail');
    cy.intercept('GET', `**/categories/${CATEGORY_ID}/view-detail*`, {
      propiedad: {
        id_propiedad: 'prop-001',
        nombre: 'Hotel Central',
        estrellas: 4,
        ubicacion: {
          ciudad: 'Bogota',
          estado_provincia: 'Cundinamarca',
          pais: 'Colombia',
          coordenadas: { lat: 4.71, lng: -74.07 },
        },
        porcentaje_impuesto: '19.00',
      },
      categoria: {
        id_categoria: CATEGORY_ID,
        nombre_comercial: 'Suite Deluxe',
        descripcion: 'Habitacion amplia',
        precio_base: { monto: '580.00', moneda: 'USD', cargo_servicio: '0.00' },
        capacidad_pax: 2,
        politica_cancelacion: { dias_anticipacion: 3, porcentaje_penalidad: '50.00' },
      },
      amenidades: [],
      galeria: [],
      rating_promedio: 4.8,
      total_resenas: 0,
      resenas: [],
    }).as('getCatalogDetail');
    cy.intercept('GET', `**/payments/by-reserva/${RESERVATION_ID}`, {
      id_pago: 'pay-001',
      id_reserva: RESERVATION_ID,
      estado: 'APPROVED',
      monto: 580,
      moneda: 'USD',
    }).as('getPayment');
    cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}/cancelacion-preview`, preview()).as('getPreview');

    cy.visit(`/mis-reservas/${RESERVATION_ID}`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
        window.localStorage.setItem('th_user_id', USER_ID);
      },
    });

    cy.wait('@getReservationDetail');
    cy.wait('@getCatalogDetail');
    cy.wait('@getPayment');
    cy.get('[data-testid="reservation-detail-cancel"]').click();
    cy.location('pathname').should('eq', `/mis-reservas/${RESERVATION_ID}/cancelar`);
    cy.wait('@getPreview', { timeout: 20000 });
    cy.get('[data-testid="cancel-keep-reservation"]').click();
    cy.location('pathname').should('eq', `/mis-reservas/${RESERVATION_ID}`);
  });

  it('loads preview and keeps processing state when PMS is pending', () => {
    cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}/cancelacion-preview`, preview()).as('getPreview');
    cy.intercept('POST', `**/api/reserva/${RESERVATION_ID}/cancelar`, {
      reservationId: RESERVATION_ID,
      reservationStatus: 'CANCELACION_EN_PROCESO',
      cancellationReference: 'CXL-BK002',
      refundAmount: 290,
      refundStatus: 'PENDING',
      processingTimeLabel: '5 a 10 dias habiles',
      pmsStatus: 'PENDING',
      mensaje: 'La cancelacion espera confirmacion del PMS.',
    }).as('cancelReservation');

    cy.visit(`/mis-reservas/${RESERVATION_ID}/cancelar`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getPreview', { timeout: 20000 });
    cy.get('[data-testid="cancel-summary"]').should('be.visible');
    cy.get('[data-testid="cancel-open-warning"]').click();
    cy.get('[data-testid="cancel-terms"]').check();
    cy.get('[data-testid="cancel-confirm"]').click();
    cy.wait('@cancelReservation');
    cy.get('[data-testid="cancel-reservation-processing"]').invoke('text').should('match', /Cancelaci[oó]n en proceso/i);
    cy.get('[data-testid="cancel-processing-reference"]').should('contain.text', 'CXL-BK002');
  });

  it('shows non cancelable preview reason', () => {
    cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}/cancelacion-preview`, preview({
      canCancel: false,
      nonCancelableReason: 'La politica ya no permite cancelacion.',
    })).as('getPreview');

    cy.visit(`/mis-reservas/${RESERVATION_ID}/cancelar`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getPreview', { timeout: 20000 });
    cy.get('[data-testid="cancel-reservation-non-cancelable"]').should('contain.text', 'La politica ya no permite cancelacion.');
    cy.get('[data-testid="cancel-open-warning"]').should('not.exist');
  });

  it('does not show success after a cancellation error', () => {
    cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}/cancelacion-preview`, preview()).as('getPreview');
    cy.intercept('POST', `**/api/reserva/${RESERVATION_ID}/cancelar`, {
      statusCode: 409,
      body: { mensaje: 'Estado invalido' },
    }).as('cancelReservation');

    cy.visit(`/mis-reservas/${RESERVATION_ID}/cancelar`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getPreview', { timeout: 20000 });
    cy.get('[data-testid="cancel-open-warning"]').click();
    cy.get('[data-testid="cancel-terms"]').check();
    cy.get('[data-testid="cancel-confirm"]').click();
    cy.wait('@cancelReservation');
    cy.get('[data-testid="cancel-submit-error"]').should('contain.text', 'Estado invalido');
    cy.get('[data-testid="cancel-reservation-success"]').should('not.exist');
  });
});
