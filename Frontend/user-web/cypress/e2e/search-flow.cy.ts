describe('Búsqueda de Hospedaje (HU-Web-01)', () => {
  beforeEach(() => {
    // Visitar la página de inicio antes de cada caso de prueba
    cy.visit('/');
  });

  it('Escenario A: Flujo Exitoso de Búsqueda', () => {
    // 1. Interceptar el autocompletado de destinos
    cy.intercept('GET', '**/v1/search/destinations?q=*', { fixture: 'search-destinations.json' }).as('getDestinations');
    
    // 2. Ingresar la ubicación y seleccionar la sugerencia
    cy.get('[data-testid="input-location"]').type('Bor');
    cy.wait('@getDestinations');
    cy.get('[data-testid="suggestion-item"]').first().click();
    cy.get('[data-testid="input-location"]').should('have.value', 'Bordeaux, Nouvelle-Aquitaine, Francia');

    // 3. Preparar fechas válidas: Ingreso mañana, Salida en 4 días
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const checkout = new Date();
    checkout.setDate(checkout.getDate() + 4);

    const checkInStr = tomorrow.toISOString().split('T')[0];
    const checkOutStr = checkout.toISOString().split('T')[0];

    cy.get('[data-testid="input-checkin"]').type(checkInStr);
    cy.get('[data-testid="input-checkout"]').type(checkOutStr);

    // 4. Modificar cantidad de huéspedes
    cy.get('[data-testid="hero-search-form"] button').contains('+').click();
    cy.get('[data-testid="guests-value"]').should('contain.text', '2');

    // 5. Interceptar los resultados de la búsqueda
    cy.intercept('GET', '**/v1/search?*', { fixture: 'search-results.json' }).as('getResults');

    // 6. Ejecutar la búsqueda
    cy.get('[data-testid="btn-search"]').click();
    cy.wait('@getResults');

    // 7. Validar la redirección y la renderización de resultados
    cy.url().should('include', '/resultados?ciudad=Bordeaux');
    cy.get('[data-testid="results-title"]').should('contain.text', 'Stays in Bordeaux');
    
    // Verificar que se renderizaron exactamente las 2 cards indicadas en el fixture
    cy.get('[data-testid="hospedaje-card"]').should('have.length', 2);
  });

  it('Escenario B: Búsqueda sin Resultados', () => {
    // Comportamiento similar preparatorio
    cy.intercept('GET', '**/v1/search/destinations?q=*', { fixture: 'search-destinations.json' }).as('getDestinations');
    cy.get('[data-testid="input-location"]').type('Bor');
    cy.wait('@getDestinations');
    cy.get('[data-testid="suggestion-item"]').first().click();

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const checkout = new Date();
    checkout.setDate(checkout.getDate() + 2);

    cy.get('[data-testid="input-checkin"]').type(tomorrow.toISOString().split('T')[0]);
    cy.get('[data-testid="input-checkout"]').type(checkout.toISOString().split('T')[0]);

    // Devolvemos 0 resultados
    cy.intercept('GET', '**/v1/search?*', { statusCode: 200, body: { resultados: [], total: 0 } }).as('getEmptyResults');

    cy.get('[data-testid="btn-search"]').click();
    cy.wait('@getEmptyResults');

    // Validar el "Empty State"
    cy.get('[data-testid="results-empty"]').should('be.visible');
    cy.get('[data-testid="results-empty-message"]').should('contain.text', 'No se encontraron hospedajes');
    
    // Probar hipervínculo de retorno
    cy.get('[data-testid="results-empty-link"]').click();
    cy.url().should('not.include', '/resultados');
  });

  it('Escenario C: Validaciones del Formulario de Búsqueda', () => {
    // Intentar realizar la búsqueda directamente sin datos
    cy.get('[data-testid="btn-search"]').click();
    
    // Como no alteramos el código HTML para añadir data-testid a los errores,
    // buscamos por la clase CSS del tooltip (rojo de fondo) y verificamos su texto
    cy.get('.bg-red-600').should('contain.text', 'Introduce un destino');
    
    // Validar control inferior de límite de huéspedes (no puede bajar de 1)
    cy.get('[data-testid="guests-value"]').should('contain.text', '1');
    cy.get('[data-testid="hero-search-form"] button').contains('−').click();
    cy.get('[data-testid="guests-value"]').should('contain.text', '1');
  });

  it('Escenario D: Verificación de Buscador Compacto y Retorno', () => {
    // Preparar fechas
    const checkIn = new Date();
    checkIn.setDate(checkIn.getDate() + 5);
    const checkOut = new Date();
    checkOut.setDate(checkOut.getDate() + 10);
    
    const fmtCheckIn = checkIn.toISOString().split('T')[0];
    const fmtCheckOut = checkOut.toISOString().split('T')[0];
    
    // Interceptar la búsqueda para que finalice el loading state
    cy.intercept('GET', '**/v1/search?*', { fixture: 'search-results.json' }).as('getResults');

    // Navegar a resultados pasando los query params
    cy.visit(`/resultados?ciudad=Cancun&fecha_inicio=${fmtCheckIn}&fecha_fin=${fmtCheckOut}&huespedes=4`);
    cy.wait('@getResults');

    // Verificar renderización y valores reflejados en la barra compacta superior
    cy.get('[data-testid="compact-search-bar"]').should('be.visible');
    cy.get('[data-testid="compact-city"]').should('contain.text', 'Cancun');
    cy.get('[data-testid="compact-guests"]').should('contain.text', '4 huéspedes');

    // Al darle clic al módulo o botón de editar búsqueda
    cy.get('[data-testid="compact-search-bar"]').click();
    
    // Debería redirigir a la pantalla principal
    cy.url().should('equal', Cypress.config().baseUrl + '/');
    
    // Validar que el state service trasladó el valor guardado
    cy.get('[data-testid="hero-search-form"]').should('be.visible');
    cy.get('[data-testid="input-location"]').should('have.value', 'Cancun');
  });
});
