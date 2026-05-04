const RESERVATION_ID = 'reserva-status-e2e-001';
const CATEGORY_ID = 'categoria-e2e-001';
const PROPERTY_ID = 'propiedad-e2e-001';

export {};

function seedAuthSession(window: Window) {
  window.localStorage.setItem('th_access_token', 'fake-access-token');
  window.localStorage.setItem('th_refresh_token', 'fake-refresh-token');
  window.localStorage.setItem('th_token_type', 'Bearer');
  window.localStorage.setItem('th_user_email', 'e2e@travelhub.com');
  window.localStorage.setItem('th_user_id', 'user-e2e-001');
}

function mockConfirmReservationSummary(bookingOverrides: Record<string, unknown> = {}) {
  cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}`, {
    body: {
      id_categoria: CATEGORY_ID,
      fecha_inicio: '2026-05-10',
      fecha_fin: '2026-05-13',
      num_huespedes: 2,
      ...bookingOverrides,
    },
  }).as('getBookingForSummary');

  cy.intercept('GET', `**/catalog/properties/by-category/${CATEGORY_ID}`, {
    fixture: 'booking-cart-catalog.json',
  }).as('getCatalogForSummary');

  cy.intercept('GET', `**/catalog/categories/${CATEGORY_ID}`, {
    fixture: 'booking-cart-category.json',
  }).as('getCategoryForSummary');

  cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}`, {
    fixture: 'booking-cart-property.json',
  }).as('getPropertyForSummary');

  cy.intercept('POST', '**/catalog/calculate-room-price', {
    fixture: 'booking-room-price.json',
  }).as('calculateRoomPriceForSummary');
}

describe('Flujos E2E de reserva (confirm, existing session, processing)', () => {
  it('Confirm reservation: muestra estado confirmado y resumen de la reserva', () => {
    mockConfirmReservationSummary({ estado: 'CONFIRMADA' });

    cy.visit(`/booking/${RESERVATION_ID}/confirm-reservation?status=confirmed&reason=Reserva%20formalizada`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getBookingForSummary');
    cy.wait('@getCatalogForSummary');
    cy.wait('@getCategoryForSummary');
    cy.wait('@getPropertyForSummary');
    cy.wait('@calculateRoomPriceForSummary');

    cy.get('[data-testid="confirm-reservation-title"]')
      .should('be.visible')
      .and('contain.text', 'Reserva Confirmada');

    cy.get('[data-testid="confirm-reservation-reason"]')
      .should('contain.text', 'Tu reserva ha sido confirmada. Se ha enviado un correo con los detalles.');

    cy.contains('Número de confirmación').should('be.visible');
    cy.contains(RESERVATION_ID).should('be.visible');

    cy.get('[data-testid="booking-summary"]')
      .should('be.visible')
      .and('contain.text', 'Hotel Mirador - Suite Familiar');
  });

  it('Confirm reservation: muestra estado rechazado por cancelación y oculta resumen', () => {
    mockConfirmReservationSummary({ estado: 'CANCELADA' });

    cy.visit(`/booking/${RESERVATION_ID}/confirm-reservation?status=rejected&reason=La%20reserva%20fue%20cancelada%20por%20inventario`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getBookingForSummary');
    cy.wait('@getCatalogForSummary');
    cy.wait('@getCategoryForSummary');
    cy.wait('@getPropertyForSummary');
    cy.wait('@calculateRoomPriceForSummary');

    cy.get('[data-testid="confirm-reservation-title"]')
      .should('be.visible')
      .and('contain.text', 'Reserva no confirmada');

    cy.get('[data-testid="confirm-reservation-reason"]')
      .should('contain.text', 'La reserva fue cancelada por inventario');

    cy.contains('Número de confirmación').should('not.exist');
    cy.get('[data-testid="booking-summary"]').should('not.exist');
    cy.contains('Volver al carrito').should('not.exist');
    cy.contains('Buscar otra opción').should('be.visible');
  });

  it('Existing session: para estado pendiente redirige al seguimiento', () => {
    cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}`, {
      body: { estado: 'PENDIENTE' },
    }).as('getPendingBooking');

    cy.visit(`/existing-session-redirect?reservationId=${RESERVATION_ID}`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getPendingBooking');

    cy.get('[data-testid="existing-session-redirect-card"]').should('be.visible');
    cy.contains('Tu reserva esta siendo procesada').should('be.visible');
    cy.contains('Abrir seguimiento de reserva').click();

    cy.location('pathname').should('eq', `/booking/${RESERVATION_ID}/processing-reservation`);
    cy.get('[data-testid="processing-reservation-card"]').should('be.visible');
  });

  it('Existing session: sin reservationId muestra fallback y permite volver a resultados', () => {
    cy.visit('/existing-session-redirect');

    cy.get('[data-testid="existing-session-redirect-card"]').should('be.visible');
    cy.contains('No encontramos una sesión activa para redirigirte.').should('be.visible');
    cy.contains('Volver a resultados').click();
    cy.location('pathname').should('eq', '/resultados');
  });

  it('Processing reservation: cuando confirma redirige a confirm-reservation con status=confirmed', () => {
    cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}`, {
      body: { estado: 'CONFIRMADA' },
    }).as('getConfirmedBooking');

    cy.visit(`/booking/${RESERVATION_ID}/processing-reservation?reason=Iniciando%20SAGA%20de%20confirmacion`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getConfirmedBooking');

    cy.location('pathname').should('eq', `/booking/${RESERVATION_ID}/confirm-reservation`);
    cy.location('search').should('include', 'status=confirmed');
    cy.get('[data-testid="confirm-reservation-title"]').should('contain.text', 'Reserva Confirmada');
  });

  it('Processing reservation: cuando cancela redirige a confirm-reservation con status=rejected', () => {
    cy.intercept('GET', `**/api/reserva/${RESERVATION_ID}`, {
      body: {
        estado: 'CANCELADA',
        motivo: 'Reserva cancelada durante el procesamiento de la SAGA',
      },
    }).as('getCancelledBooking');

    cy.visit(`/booking/${RESERVATION_ID}/processing-reservation`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getCancelledBooking');

    cy.location('pathname').should('eq', `/booking/${RESERVATION_ID}/confirm-reservation`);
    cy.location('search').should('include', 'status=rejected');

    cy.get('[data-testid="confirm-reservation-title"]').should('contain.text', 'Reserva no confirmada');
    cy.get('[data-testid="confirm-reservation-reason"]').should('contain.text', 'Estamos procesando tu reserva');
  });
});
