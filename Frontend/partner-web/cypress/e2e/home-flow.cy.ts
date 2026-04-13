describe('Home y Navegación del Partner (HU-Partner-Home)', () => {
  /**
   * Helper: simula sesión autenticada inyectando tokens en localStorage.
   */
  function visitHomeAuthenticated(fixture = 'current-user.json') {
    cy.intercept('GET', '**/auth/me', { fixture }).as('getMe');

    cy.visit('/', {
      onBeforeLoad(window) {
        window.localStorage.setItem('access_token', 'fake-jwt-token');
        window.localStorage.setItem('refresh_token', 'fake-refresh-token');
      },
    });

    cy.wait('@getMe');
  }

  it('Escenario A: Muestra el perfil del usuario con hotel asignado', () => {
    visitHomeAuthenticated('current-user.json');

    // Verificar la tarjeta de bienvenida
    cy.get('[data-testid="welcome-card"]').should('be.visible');
    cy.get('[data-testid="welcome-title"]').should('contain.text', 'socio@hotel.com');

    // Verificar que se muestra el badge del partner
    cy.get('.partner-badge').should('contain.text', 'partner-hotel-001');
  });

  it('Escenario B: Muestra mensaje cuando el usuario no tiene hotel', () => {
    visitHomeAuthenticated('current-user-no-partner.json');

    cy.get('[data-testid="welcome-card"]').should('be.visible');
    cy.get('[data-testid="welcome-title"]').should('contain.text', 'admin@sinhotel.com');

    // Verificar mensaje "sin hotel"
    cy.get('.no-partner').should('contain.text', 'No tienes un hotel asignado');
  });

  it('Escenario C: Muestra error si falla la carga del perfil', () => {
    cy.intercept('GET', '**/auth/me', { statusCode: 500, body: {} }).as('getMeFail');

    cy.visit('/', {
      onBeforeLoad(window) {
        window.localStorage.setItem('access_token', 'fake-jwt-token');
        window.localStorage.setItem('refresh_token', 'fake-refresh-token');
      },
    });

    cy.wait('@getMeFail');

    // Verificar estado de error
    cy.get('[data-testid="welcome-error"]').should('be.visible');
    cy.get('[data-testid="welcome-error"]').should('contain.text', 'No se pudo cargar la información del usuario');

    // Verificar que no se muestra la tarjeta de bienvenida
    cy.get('[data-testid="welcome-card"]').should('not.exist');
  });

  it('Escenario D: Muestra estado de carga mientras se obtiene el perfil', () => {
    cy.intercept('GET', '**/auth/me', {
      fixture: 'current-user.json',
      delay: 1000,
    }).as('getMeSlow');

    cy.visit('/', {
      onBeforeLoad(window) {
        window.localStorage.setItem('access_token', 'fake-jwt-token');
        window.localStorage.setItem('refresh_token', 'fake-refresh-token');
      },
    });

    // Verificar spinner de carga
    cy.get('[data-testid="welcome-loading"]').should('be.visible');

    // Esperar a que termine y verificar que el loading desaparece
    cy.wait('@getMeSlow');
    cy.get('[data-testid="welcome-loading"]').should('not.exist');
    cy.get('[data-testid="welcome-card"]').should('be.visible');
  });

  it('Escenario E: Logout desde el navbar redirige a /login', () => {
    visitHomeAuthenticated('current-user.json');

    // 1. Abrir el dropdown del menú
    cy.get('.user-menu-btn').click();
    cy.get('[data-testid="navbar-dropdown"]').should('be.visible');

    // 2. Hacer clic en "Cerrar sesión"
    cy.get('[data-testid="btn-logout"]').click();

    // 3. Verificar redirección al login
    cy.url().should('include', '/login');

    // 4. Verificar que se limpiaron los tokens
    cy.window().its('localStorage').invoke('getItem', 'access_token').should('be.null');
    cy.window().its('localStorage').invoke('getItem', 'refresh_token').should('be.null');
  });
});
