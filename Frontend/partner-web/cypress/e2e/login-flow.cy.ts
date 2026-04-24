describe('Login de Partner (HU-Partner-Login)', () => {
  beforeEach(() => {
    // Limpiar localStorage para comenzar sin sesión
    cy.visit('/login', {
      onBeforeLoad(window) {
        window.localStorage.clear();
      },
    });
  });

  it('Escenario A: Login exitoso redirige al Home', () => {
    // 1. Interceptar la petición de login al backend
    cy.intercept('POST', '**/auth/login', { fixture: 'login-success.json' }).as('loginRequest');

    // 2. Interceptar la petición de perfil del usuario (se llama al cargar Home)
    cy.intercept('GET', '**/auth/me', { fixture: 'current-user.json' }).as('getCurrentUser');

    // 3. Llenar el formulario
    cy.get('[data-testid="input-email"]').type('socio@hotel.com');
    cy.get('[data-testid="input-password"]').type('123456');

    // 4. Ejecutar el login
    cy.get('[data-testid="btn-login"]').click();
    cy.wait('@loginRequest');

    // 5. Verificar que se envió el body correcto al backend
    cy.get('@loginRequest').its('request.body').should('deep.equal', {
      email: 'socio@hotel.com',
      password: '123456',
    });

    // 6. Verificar redirección al Home
    cy.url().should('eq', Cypress.config().baseUrl + '/');

    // 7. Verificar tokens almacenados en localStorage
    cy.window().its('localStorage').invoke('getItem', 'access_token').should('not.be.null');
    cy.window().its('localStorage').invoke('getItem', 'refresh_token').should('not.be.null');

    // 8. Verificar que se cargó el perfil del usuario
    cy.wait('@getCurrentUser');
    cy.get('[data-testid="welcome-card"]').should('be.visible');
    cy.get('[data-testid="welcome-title"]').should('contain.text', 'socio@hotel.com');
  });

  it('Escenario B: Login con credenciales incorrectas muestra error', () => {
    // 1. Interceptar con error 401
    cy.intercept('POST', '**/auth/login', {
      statusCode: 401,
      fixture: 'login-error.json',
    }).as('loginFailed');

    // 2. Llenar y enviar el formulario
    cy.get('[data-testid="input-email"]').type('socio@hotel.com');
    cy.get('[data-testid="input-password"]').type('claveIncorrecta');
    cy.get('[data-testid="btn-login"]').click();
    cy.wait('@loginFailed');

    // 3. Verificar que se muestra el banner de error
    cy.get('[data-testid="login-error"]').should('be.visible');
    cy.get('[data-testid="login-error"]').should('contain.text', 'Correo o contraseña incorrectos');

    // 4. Verificar que NO se redirigió
    cy.url().should('include', '/login');

    // 5. Verificar que no se almacenó token
    cy.window().its('localStorage').invoke('getItem', 'access_token').should('be.null');
  });

  it('Escenario C: Botón de login deshabilitado con formulario inválido', () => {
    // 1. Verificar que el botón está deshabilitado sin datos
    cy.get('[data-testid="btn-login"]').should('be.disabled');

    // 2. Ingresar solo email (sin contraseña)
    cy.get('[data-testid="input-email"]').type('socio@hotel.com');
    cy.get('[data-testid="btn-login"]').should('be.disabled');

    // 3. Limpiar email, ingresar solo contraseña
    cy.get('[data-testid="input-email"]').clear();
    cy.get('[data-testid="input-password"]').type('123456');
    cy.get('[data-testid="btn-login"]').should('be.disabled');

    // 4. Ingresar email inválido + contraseña
    cy.get('[data-testid="input-email"]').type('no-es-un-email');
    cy.get('[data-testid="btn-login"]').should('be.disabled');

    // 5. Corregir email: ahora debería habilitarse
    cy.get('[data-testid="input-email"]').clear().type('socio@hotel.com');
    cy.get('[data-testid="btn-login"]').should('not.be.disabled');
  });

  it('Escenario D: Guard redirige a /login si no hay sesión activa', () => {
    // Intentar acceder al Home sin autenticación
    cy.visit('/');

    // Verificar que el guard redirige al login
    cy.url().should('include', '/login');
  });

  it('Escenario E: Login muestra estado de carga durante la petición', () => {
    // 1. Interceptar con delay para ver el loading
    cy.intercept('POST', '**/auth/login', {
      fixture: 'login-success.json',
      delay: 1000,
    }).as('loginSlow');

    cy.intercept('GET', '**/auth/me', { fixture: 'current-user.json' }).as('getCurrentUser');

    // 2. Llenar y enviar
    cy.get('[data-testid="input-email"]').type('socio@hotel.com');
    cy.get('[data-testid="input-password"]').type('123456');
    cy.get('[data-testid="btn-login"]').click();

    // 3. Verificar estado de carga
    cy.get('[data-testid="login-loading"]').should('be.visible');
    cy.get('[data-testid="btn-login"]').should('be.disabled');

    // 4. Esperar a que se complete y verificar redirección
    cy.wait('@loginSlow');
    cy.url().should('eq', Cypress.config().baseUrl + '/');
  });
});
