const BOOKING_ID = 'reserva-e2e-001';
const CATEGORY_ID = 'categoria-e2e-001';
const PROPERTY_ID = 'propiedad-e2e-001';

const bookingResponse = {
  id_usuario: 'usuario-e2e-001',
  id_categoria: CATEGORY_ID,
  fecha_inicio: '2026-05-10',
  fecha_fin: '2026-05-13',
  num_huespedes: 2,
};

const categoryResponse = {
  id_categoria: CATEGORY_ID,
  id_propiedad: PROPERTY_ID,
  nombre_comercial: 'Suite Familiar',
  foto_portada_url: 'https://images.example.com/suite-familiar.jpg',
  precio_base: {
    monto: 150,
    moneda: 'USD',
  },
};

const catalogResponse = {
  id_propiedad: PROPERTY_ID,
  nombre: 'Hotel Mirador',
  propiedad_nombre: 'Hotel Mirador',
  ciudad: 'Cartagena',
  pais: 'Colombia',
  imagen_principal_url: 'https://images.example.com/hotel-mirador.jpg',
  precio_base: '150',
};

const propertyResponse = {
  id_propiedad: PROPERTY_ID,
  nombre: 'Hotel Mirador',
  ubicacion: {
    ciudad: 'Cartagena',
    pais: 'Colombia',
  },
};

const propertyCategoriesResponse = [
  {
    id_categoria: CATEGORY_ID,
    codigo_mapeo_pms: 'CAT-001',
    categoria_nombre: 'Suite Familiar',
    precio_base: 150,
    moneda: 'USD',
    capacidad_pax: 2,
    imagen_principal_url: 'https://images.example.com/suite-familiar.jpg',
    amenidades_destacadas: ['Wifi'],
  },
];

function mockBookingCartRequests() {
  cy.intercept('GET', `**/api/reserva/${BOOKING_ID}`, bookingResponse).as('getBooking');
  cy.intercept('GET', `**/catalog/properties/by-category/${CATEGORY_ID}`, catalogResponse).as('getCatalog');
  cy.intercept('GET', `**/catalog/categories/${CATEGORY_ID}`, categoryResponse).as('getCategory');
  cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}`, propertyResponse).as('getProperty');
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

describe('Booking Cart Page (HU-Web Booking)', () => {
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

    cy.get('[data-testid="input-name"]').type('Maria');
    cy.get('[data-testid="input-lastname"]').type('Diaz');
    cy.get('[data-testid="input-email"]').type('maria@example.com');
    cy.get('[data-testid="input-phone"]').type('3001234567');
    cy.get('[data-testid="input-request"]').type('Necesito check-in temprano.');

    cy.get('[data-testid="input-name"]').should('have.value', 'Maria');
    cy.get('[data-testid="input-lastname"]').should('have.value', 'Diaz');
    cy.get('[data-testid="input-email"]').should('have.value', 'maria@example.com');
    cy.get('[data-testid="input-phone"]').should('have.value', '3001234567');
    cy.get('[data-testid="input-request"]').should('have.value', 'Necesito check-in temprano.');
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

      req.reply({
        statusCode: 201,
        body: {
          id_reserva: 'hold-backend-001',
          mensaje: 'Reserva creada',
        },
      });
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
      statusCode: 200,
      body: { mensaje: 'Reserva expirada' },
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

    cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}/categories`, propertyCategoriesResponse).as('getPropertyCategories');

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
      body: { mensaje: 'No hay cupos disponibles' },
    }).as('createHoldError');

    const alertStub = cy.stub();
    cy.on('window:alert', alertStub);

    cy.get('[data-testid="continue-payment-btn"]').click();
    cy.wait('@createHoldError');

    cy.wrap(alertStub).should('have.been.calledWith', 'No hay cupos disponibles');
    cy.get('[data-testid="continue-payment-btn"]').should('not.be.disabled');
  });
});