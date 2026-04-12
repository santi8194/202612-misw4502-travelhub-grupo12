const PROPERTY_ID = 'propiedad-e2e-001';
const CATEGORY_ID = 'categoria-e2e-001';

export {};

function visitPropertyDetail() {
  cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}`, { fixture: 'booking-cart-property.json' }).as('getProperty');
  cy.intercept('GET', `**/catalog/properties/${PROPERTY_ID}/categories`, { fixture: 'booking-cart-property-categories.json' }).as('getCategories');

  cy.visit(`/property/${PROPERTY_ID}?fecha_inicio=2026-05-10&fecha_fin=2026-05-13&huespedes=2&id_categoria=${CATEGORY_ID}`, {
    onBeforeLoad(window) {
      window.localStorage.clear();
    },
  });

  cy.wait(['@getProperty', '@getCategories']);
  cy.get('[data-testid="property-detail-card"]').should('be.visible');
}

describe('Detalle de Propiedad - errores de reserva', () => {
  it('Escenario A: muestra un mensaje claro cuando la categoria no existe', () => {
    visitPropertyDetail();

    cy.intercept('POST', '**/api/reserva', {
      statusCode: 404,
      fixture: 'booking-cart-create-hold-category-missing.json',
    }).as('createBookingCategoryMissing');

    cy.get('[data-testid="property-detail-reservar"]').click();
    cy.wait('@createBookingCategoryMissing');

    cy.get('[data-testid="property-detail-error"]')
      .should('be.visible')
      .and('contain.text', 'La categoria no existe');
    cy.location('pathname').should('eq', `/property/${PROPERTY_ID}`);
  });

  it('Escenario B: informa falta de disponibilidad sin dejar un mensaje genérico', () => {
    visitPropertyDetail();

    cy.intercept('POST', '**/api/reserva', {
      statusCode: 409,
      fixture: 'booking-cart-create-hold-error.json',
    }).as('createBookingNoAvailability');

    cy.get('[data-testid="property-detail-reservar"]').click();
    cy.wait('@createBookingNoAvailability');

    cy.get('[data-testid="property-detail-error"]')
      .should('be.visible')
      .and('contain.text', 'No hay cupos disponibles');
  });

  it('Escenario C: conserva un mensaje específico del backend cuando aporta más contexto', () => {
    visitPropertyDetail();

    cy.intercept('POST', '**/api/reserva', {
      statusCode: 400,
      fixture: 'booking-cart-create-hold-specific-message.json',
    }).as('createBookingSpecificMessage');

    cy.get('[data-testid="property-detail-reservar"]').click();
    cy.wait('@createBookingSpecificMessage');

    cy.get('[data-testid="property-detail-error"]')
      .should('be.visible')
      .and('contain.text', 'La tarifa configurada para la reserva ya no está vigente.');
  });

  it('Escenario D: si el backend responde sin id_reserva pero con error de inventario, muestra el mensaje específico', () => {
    visitPropertyDetail();

    cy.intercept('POST', '**/api/reserva', {
      statusCode: 200,
      fixture: 'booking-cart-create-hold-inventory-date-error.json',
    }).as('createBookingInventoryError');

    cy.get('[data-testid="property-detail-reservar"]').click();
    cy.wait('@createBookingInventoryError');

    cy.get('[data-testid="property-detail-error"]')
      .should('be.visible')
      .and('contain.text', 'No existe inventario para la categoria en la fecha 2026-04-12');
  });
});