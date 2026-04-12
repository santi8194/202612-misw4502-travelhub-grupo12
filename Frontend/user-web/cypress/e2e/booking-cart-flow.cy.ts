const BOOKING_ID = 'reserva-e2e-001';
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

function mockBookingCartRequests() {
  cy.intercept('GET', `**/api/reserva/${BOOKING_ID}`, { fixture: 'booking-cart-booking.json' }).as('getBooking');
  cy.intercept('GET', `**/catalog/properties/by-category/${CATEGORY_ID}`, { fixture: 'booking-cart-catalog.json' }).as('getCatalog');
  cy.intercept('GET', `**/catalog/categories/${CATEGORY_ID}`, { fixture: 'booking-cart-category.json' }).as('getCategory');
  cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}`, { fixture: 'booking-cart-property.json' }).as('getProperty');
}

function visitBookingCart() {
  mockBookingCartRequests();

  cy.visit(`/booking/${BOOKING_ID}`, {
    onBeforeLoad(window) {
      window.localStorage.clear();
    },
  });

  cy.wait(['@getBooking', '@getCatalog', '@getCategory', '@getProperty']);
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

    cy.get('[data-testid="booking-total"]').should('contain.text', '$495');

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

  it('Escenario B: envía la solicitud de hold con los datos esperados', () => {
    visitBookingCart();

    cy.intercept('POST', '**/api/reserva', (req) => {
      expect(req.body).to.include({
        id_categoria: CATEGORY_ID,
        fecha_check_in: '2026-05-10',
        fecha_check_out: '2026-05-13',
      });
      expect(req.body.ocupacion).to.deep.equal({
        adultos: 2,
        ninos: 0,
        infantes: 0,
      });

      req.reply({ fixture: 'booking-cart-create-hold-success.json' });
    }).as('createHold');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    cy.get('[data-testid="continue-payment-btn"]').click();
    cy.wait('@createHold');

    cy.get('[data-testid="hold-timer"]').should('be.visible');
    cy.wrap(alertStub).should('not.have.been.called');
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
      },
    });

    cy.wait(['@getBooking', '@getCatalog', '@getCategory', '@getProperty']);
    cy.get('[data-testid="hold-timer"]').should('be.visible');

    cy.tick(15 * 60 * 1000);
    cy.wait('@expireBooking');

    cy.get('[data-testid="hold-timer-expired"]').should('be.visible');
    cy.get('[data-testid="continue-payment-btn"]').should('be.disabled');
    cy.wrap(alertStub).should('have.been.calledWith', 'El hold expiró');
  });

  it('Escenario D: vuelve al detalle de la propiedad con los parámetros de la reserva', () => {
    visitBookingCart();

    cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}/categories`, { fixture: 'booking-cart-property-categories.json' }).as('getPropertyCategories');

    cy.get('[data-testid="back-link"]').click();

    cy.wait('@getProperty');
    cy.wait('@getPropertyCategories');

    cy.location('pathname').should('eq', `/property/${PROPERTY_ID}`);
    cy.location('search')
      .should('include', `id_categoria=${CATEGORY_ID}`)
      .and('include', 'fecha_inicio=2026-05-10')
      .and('include', 'fecha_fin=2026-05-13')
      .and('include', 'huespedes=2');
  });

  it('Escenario E: muestra una alerta cuando el backend rechaza la creación del hold', () => {
    visitBookingCart();

    cy.intercept('POST', '**/api/reserva', {
      statusCode: 409,
      fixture: 'booking-cart-create-hold-error.json',
    }).as('createHoldError');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    cy.get('[data-testid="continue-payment-btn"]').click();
    cy.wait('@createHoldError');

    cy.wrap(alertStub).should(
      'have.been.calledWith',
      'Ya no hay disponibilidad para las fechas seleccionadas. Elige otra categoria o cambia las fechas.'
    );
    cy.get('[data-testid="booking-cart-error"]')
      .should('be.visible')
      .and('contain.text', 'Ya no hay disponibilidad para las fechas seleccionadas.');
    cy.get('[data-testid="continue-payment-btn"]').should('not.be.disabled');
  });

  it('Escenario F: informa cuando la categoria ya no existe', () => {
    visitBookingCart();

    cy.intercept('POST', '**/api/reserva', {
      statusCode: 404,
      fixture: 'booking-cart-create-hold-category-missing.json',
    }).as('createHoldCategoryMissing');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    cy.get('[data-testid="continue-payment-btn"]').click();
    cy.wait('@createHoldCategoryMissing');

    cy.wrap(alertStub).should(
      'have.been.calledWith',
      'La categoria seleccionada no existe o ya no está disponible. Regresa y elige otra opción.'
    );
    cy.get('[data-testid="booking-cart-error"]')
      .should('be.visible')
      .and('contain.text', 'La categoria seleccionada no existe o ya no está disponible.');
  });

  it('Escenario G: respeta un mensaje específico del backend cuando es más útil', () => {
    visitBookingCart();

    cy.intercept('POST', '**/api/reserva', {
      statusCode: 400,
      fixture: 'booking-cart-create-hold-specific-message.json',
    }).as('createHoldSpecificError');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    cy.get('[data-testid="continue-payment-btn"]').click();
    cy.wait('@createHoldSpecificError');

    cy.wrap(alertStub).should('have.been.calledWith', 'La tarifa configurada para la reserva ya no está vigente.');
    cy.get('[data-testid="booking-cart-error"]')
      .should('be.visible')
      .and('contain.text', 'La tarifa configurada para la reserva ya no está vigente.');
    cy.get('[data-testid="continue-payment-btn"]').should('not.be.disabled');
  });
});