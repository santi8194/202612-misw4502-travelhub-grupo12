const BOOKING_ID = 'reserva-e2e-001';
const OTHER_BOOKING_ID = 'reserva-e2e-002';
const CATEGORY_ID = 'categoria-e2e-001';
const PROPERTY_ID = 'propiedad-e2e-001';

export {};

const guestForm = {
  name: 'Maria',
  lastName: 'Diaz',
  email: 'maria@example.com',
  phone: '3001234567',
  request: 'Necesito check-in temprano.',
};

const BOOKING_SIGNATURE = `${CATEGORY_ID}|2026-05-10|2026-05-13|2`;

function holdKey(reservationId: string) {
  return `hold:${reservationId}`;
}

function sessionKey(signature: string) {
  return `booking-session:${signature}`;
}

function seedAuthSession(window: Window) {
  window.localStorage.setItem('th_access_token', 'fake-access-token');
  window.localStorage.setItem('th_refresh_token', 'fake-refresh-token');
  window.localStorage.setItem('th_token_type', 'Bearer');
  window.localStorage.setItem('th_user_email', 'e2e@travelhub.com');
  window.localStorage.setItem('th_user_id', 'user-e2e-001');
}

function mockBookingCartRequests(reservationId = BOOKING_ID) {
  cy.intercept('GET', `**/api/reserva/${reservationId}`, { fixture: 'booking-cart-booking.json' }).as(`getBooking-${reservationId}`);
  cy.intercept('GET', `**/catalog/properties/by-category/${CATEGORY_ID}`, { fixture: 'booking-cart-catalog.json' }).as('getCatalog');
  cy.intercept('GET', `**/catalog/categories/${CATEGORY_ID}`, { fixture: 'booking-cart-category.json' }).as('getCategory');
  cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}`, { fixture: 'booking-cart-property.json' }).as('getProperty');
  cy.intercept('POST', '**/catalog/calculate-room-price', { fixture: 'booking-room-price.json' }).as('calculateRoomPrice');
}

function visitBookingCart(reservationId = BOOKING_ID) {
  mockBookingCartRequests(reservationId);

  cy.visit(`/booking/${reservationId}`, {
    onBeforeLoad(window) {
      window.localStorage.clear();
      seedAuthSession(window);
    },
  });

  cy.wait([`@getBooking-${reservationId}`, '@getCatalog', '@getCategory', '@getProperty', '@calculateRoomPrice']);
}

function fillGuestForm() {
  cy.get('[data-testid="input-name"]').type(guestForm.name);
  cy.get('[data-testid="input-lastname"]').type(guestForm.lastName);
  cy.get('[data-testid="input-email"]').type(guestForm.email);
  cy.get('[data-testid="input-phone"]').type(guestForm.phone);
}

function mockFormalizeBooking(reservationId = BOOKING_ID) {
  cy.intercept('POST', `**/api/reserva/${reservationId}/formalizar`, {
    body: {
      mensaje: 'Tu reserva está siendo procesada por la saga.',
      pago: {
        id_pago: 'mock-pago-123',
        id_reserva: reservationId,
        referencia: 'mock-ref',
        estado: 'PENDIENTE',
        monto: 495,
        moneda: 'COP',
        checkout: {
          public_key: 'pub_test_123',
          currency: 'COP',
          amount_in_cents: 49500,
          reference: 'mock-ref',
          signature_integrity: 'mock-sig'
        }
      }
    },
  }).as(`formalizeBooking-${reservationId}`);
}

describe('Carrito de Reserva (HU-Web-BookingCart)', () => {
  it('Escenario A: carga el resumen y permite diligenciar los datos del huésped', () => {
    visitBookingCart();

    cy.get('[data-testid="stepper"]').should('be.visible');
    cy.get('[data-testid="guest-details-card"]').should('be.visible');
    cy.get('[data-testid="hold-timer"]').should('be.visible');

    cy.get('[data-testid="booking-summary"]')
      .should('contain.text', 'Hotel Mirador - Suite Familiar')
      .and('contain.text', 'Cartagena, Colombia')
      .and('contain.text', '2026-05-10')
      .and('contain.text', '2026-05-13')
      .and('contain.text', '2')
      .and('contain.text', '3');

    cy.get('[data-testid="booking-total"]').should('contain.text', '495');

    cy.get('[data-testid="input-name"]').type(guestForm.name);
    cy.get('[data-testid="input-lastname"]').type(guestForm.lastName);
    cy.get('[data-testid="input-email"]').type(guestForm.email);
    cy.get('[data-testid="input-phone"]').type(guestForm.phone);
    cy.get('[data-testid="input-request"]').type(guestForm.request);

    cy.get('[data-testid="input-name"]').should('have.value', guestForm.name);
    cy.get('[data-testid="input-lastname"]').should('have.value', guestForm.lastName);
    cy.get('[data-testid="input-email"]').should('have.value', guestForm.email);
    cy.get('[data-testid="input-phone"]').should('have.value', guestForm.phone);
    cy.get('[data-testid="input-request"]').should('have.value', guestForm.request);
    cy.get('[data-testid="continue-payment-btn"]').should('not.be.disabled');
  });

  it('Escenario B: reutiliza la reserva actual y no crea una nueva al continuar', () => {
    visitBookingCart();
    mockFormalizeBooking();

    cy.intercept('POST', '**/api/reserva', { statusCode: 500, body: { mensaje: 'No debería invocarse desde booking cart' } }).as('createHold');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    fillGuestForm();

    cy.get('[data-testid="continue-payment-btn"]').click();

    cy.wait('@formalizeBooking-reserva-e2e-001');
    cy.window().its('localStorage').invoke('getItem', sessionKey(BOOKING_SIGNATURE)).should('not.be.null');
    cy.get('@createHold.all').should('have.length', 0);
    cy.wrap(alertStub).should('not.have.been.called');
    cy.location('pathname').should('eq', `/booking/${BOOKING_ID}/payment`);
  });

  it('Escenario C: expira el hold y bloquea la continuación del pago', () => {
    cy.clock(new Date('2026-04-12T12:00:00Z').getTime(), ['Date', 'setInterval', 'clearInterval']);
    mockBookingCartRequests();
    cy.intercept('POST', `**/api/reserva/${BOOKING_ID}/expirar`, {
      fixture: 'booking-cart-expire-success.json',
    }).as('expireBooking');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    cy.visit(`/booking/${BOOKING_ID}`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait([`@getBooking-${BOOKING_ID}`, '@getCatalog', '@getCategory', '@getProperty', '@calculateRoomPrice']);
    cy.get('[data-testid="hold-timer"]').should('be.visible');

    cy.tick(15 * 60 * 1000);
    cy.wait('@expireBooking');

    cy.get('[data-testid="hold-timer-expired"]').should('be.visible');
    cy.get('[data-testid="continue-payment-btn"]').should('be.disabled');
    cy.wrap(alertStub).should('not.have.been.called');
  });

  it('Escenario D: vuelve al detalle de la categoría con los parámetros de la reserva', () => {
    visitBookingCart();

    cy.window().then((window) => {
      Object.defineProperty(window.history, 'length', {
        configurable: true,
        value: 1,
      });
    });

    cy.get('[data-testid="back-link"]').click();

    cy.location('pathname').should('eq', `/category/${CATEGORY_ID}`);
    cy.location('search')
      .should('include', 'fecha_inicio=2026-05-10')
      .and('include', 'fecha_fin=2026-05-13')
      .and('include', 'huespedes=2');
  });

  it('Escenario E: reutiliza la sesión activa de la misma reserva sin duplicar solicitudes', () => {
    visitBookingCart();
    mockFormalizeBooking();

    const expiresAt = Date.now() + 10 * 60 * 1000;
    cy.window().then((window) => {
      window.localStorage.setItem(holdKey(BOOKING_ID), JSON.stringify({ id: BOOKING_ID, expiresAt }));
      window.localStorage.setItem(sessionKey(BOOKING_SIGNATURE), JSON.stringify({
        reservationId: BOOKING_ID,
        signature: BOOKING_SIGNATURE,
        expiresAt,
      }));
    });

    cy.intercept('POST', '**/api/reserva', { statusCode: 500, body: { mensaje: 'No debería invocarse desde booking cart' } }).as('createHoldError');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    fillGuestForm();

    cy.get('[data-testid="continue-payment-btn"]').click();

    cy.wait('@formalizeBooking-reserva-e2e-001');
    cy.get('@createHoldError.all').should('have.length', 0);
    cy.wrap(alertStub).should('not.have.been.called');
    cy.location('pathname').should('eq', `/booking/${BOOKING_ID}/payment`);
  });

  it('Escenario F: redirige a la reserva activa si ya existe otra con la misma información', () => {
    mockBookingCartRequests();
    mockBookingCartRequests(OTHER_BOOKING_ID);

    cy.visit(`/booking/${BOOKING_ID}`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
        window.localStorage.setItem(sessionKey(BOOKING_SIGNATURE), JSON.stringify({
          reservationId: OTHER_BOOKING_ID,
          signature: BOOKING_SIGNATURE,
          expiresAt: Date.now() + 10 * 60 * 1000,
        }));
      },
    });

    cy.wait([`@getBooking-${BOOKING_ID}`, '@getCatalog', '@getCategory', '@getProperty', '@calculateRoomPrice']);
    cy.location('pathname').should('eq', `/booking/${OTHER_BOOKING_ID}`);
  });

  it('Escenario G: mantiene timers independientes por id de reserva', () => {
    visitBookingCart();

    cy.window().then((window) => {
      window.localStorage.setItem(holdKey(BOOKING_ID), JSON.stringify({ id: BOOKING_ID, expiresAt: Date.now() + 9 * 60 * 1000 }));
      window.localStorage.setItem(holdKey(OTHER_BOOKING_ID), JSON.stringify({ id: OTHER_BOOKING_ID, expiresAt: Date.now() + 3 * 60 * 1000 }));
    });

    cy.reload();
    cy.wait([`@getBooking-${BOOKING_ID}`, '@getCatalog', '@getCategory', '@getProperty', '@calculateRoomPrice']);

    cy.window().then((window) => {
      expect(window.localStorage.getItem(holdKey(BOOKING_ID))).to.not.equal(window.localStorage.getItem(holdKey(OTHER_BOOKING_ID)));
    });
    cy.get('[data-testid="hold-timer"]').should('be.visible');
  });
});