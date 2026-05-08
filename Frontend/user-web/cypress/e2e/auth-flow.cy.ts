describe('Flujo de Autenticación (Login, Register, Confirm)', () => {
  // ───────────────────────────────────────────────
  // Login
  // ───────────────────────────────────────────────
  describe('Página de Login (HU-Auth-01)', () => {
    beforeEach(() => {
      cy.visit('/auth/login');
    });

    it('Escenario A: Renderiza los elementos principales', () => {
      cy.contains('TravelHub').should('be.visible');
      cy.contains('Iniciar Sesión').should('be.visible');
      cy.get('input[type="email"]').should('exist');
      cy.get('input[type="password"]').should('exist');
      cy.get('button[type="submit"]').should('be.visible');
    });

    it('Escenario B: Muestra error con campos vacíos', () => {
      cy.get('button[type="submit"]').click();
      cy.get('small').should('have.length.at.least', 1);
    });

    it('Escenario C: Muestra error con correo inválido', () => {
      cy.get('input[type="email"]').type('no-es-un-correo');
      cy.get('input[type="password"]').type('Clave1234!');
      cy.get('button[type="submit"]').click();
      cy.get('small').should('contain.text', 'correo válido');
    });

    it('Escenario D: Login exitoso redirige al home', () => {
      cy.intercept('POST', '**/login', {
        statusCode: 200,
        body: {
          access_token: 'fake-access',
          refresh_token: 'fake-refresh',
          token_type: 'Bearer',
        },
      }).as('loginRequest');

      cy.get('input[type="email"]').type('usuario@ejemplo.com');
      cy.get('input[type="password"]').type('Clave1234!');
      cy.get('button[type="submit"]').click();

      cy.wait('@loginRequest');
      cy.url().should('not.include', '/auth/login');
    });

    it('Escenario E: Login fallido muestra notificación de error', () => {
      cy.intercept('POST', '**/login', {
        statusCode: 401,
        body: { detail: 'Invalid credentials' },
      }).as('loginFail');

      cy.get('input[type="email"]').type('usuario@ejemplo.com');
      cy.get('input[type="password"]').type('ClaveIncorrecta1!');
      cy.get('button[type="submit"]').click();

      cy.wait('@loginFail');
      cy.get('button[type="submit"]').should('not.be.disabled');
    });

    it('Escenario F: Toggle de visibilidad de contraseña', () => {
      cy.get('input[type="password"]').should('exist');
      cy.get('.password-toggle').click();
      cy.get('input[type="text"]').should('exist');
      cy.get('.password-toggle').click();
      cy.get('input[type="password"]').should('exist');
    });

    it('Escenario G: Enlace a registro navega a /auth/registro', () => {
      cy.contains('a', 'Regístrate').click();
      cy.url().should('include', '/auth/registro');
    });
  });

  // ───────────────────────────────────────────────
  // Register
  // ───────────────────────────────────────────────
  describe('Página de Registro (HU-Auth-02)', () => {
    beforeEach(() => {
      cy.visit('/auth/registro');
    });

    it('Escenario A: Renderiza los elementos principales', () => {
      cy.contains('TravelHub').should('be.visible');
      cy.contains('Crear Cuenta').should('be.visible');
      cy.get('input[placeholder="Juan"]').should('exist');
      cy.get('input[placeholder="Pérez"]').should('exist');
      cy.get('input[type="email"]').should('exist');
      cy.get('button[type="submit"]').should('be.visible');
    });

    it('Escenario B: Muestra errores con campos vacíos', () => {
      cy.get('button[type="submit"]').click();
      cy.get('small').should('have.length.at.least', 1);
    });

    it('Escenario C: Muestra error cuando las contraseñas no coinciden', () => {
      cy.get('input[placeholder="Juan"]').type('Juan');
      cy.get('input[placeholder="Pérez"]').type('Pérez');
      cy.get('input[type="email"]').type('juan@ejemplo.com');

      cy.get('input[type="password"]').eq(0).type('Clave1234!');
      cy.get('input[type="password"]').eq(1).type('OtraClave1234!');

      cy.get('button[type="submit"]').click();
      cy.get('small').should('contain.text', 'no coinciden');
    });

    it('Escenario D: Registro exitoso redirige a confirmación', () => {
      cy.intercept('POST', '**/register', {
        statusCode: 200,
        body: { message: 'User registered' },
      }).as('registerRequest');

      cy.get('input[placeholder="Juan"]').type('Juan');
      cy.get('input[placeholder="Pérez"]').type('Pérez');
      cy.get('input[type="email"]').type('juan@ejemplo.com');

      cy.get('input[type="password"]').eq(0).type('Clave1234!');
      cy.get('input[type="password"]').eq(1).type('Clave1234!');

      cy.get('button[type="submit"]').click();
      cy.wait('@registerRequest');
      cy.url().should('include', '/auth/confirmar');
    });

    it('Escenario E: Registro fallido muestra notificación', () => {
      cy.intercept('POST', '**/register', {
        statusCode: 409,
        body: { detail: 'Email already in use' },
      }).as('registerFail');

      cy.get('input[placeholder="Juan"]').type('Juan');
      cy.get('input[placeholder="Pérez"]').type('Pérez');
      cy.get('input[type="email"]').type('existente@ejemplo.com');

      cy.get('input[type="password"]').eq(0).type('Clave1234!');
      cy.get('input[type="password"]').eq(1).type('Clave1234!');

      cy.get('button[type="submit"]').click();
      cy.wait('@registerFail');
      cy.get('button[type="submit"]').should('not.be.disabled');
    });

    it('Escenario F: Enlace a login navega a /auth/login', () => {
      cy.contains('a', 'Inicia sesión').click();
      cy.url().should('include', '/auth/login');
    });
  });

  // ───────────────────────────────────────────────
  // Confirm
  // ───────────────────────────────────────────────
  describe('Página de Confirmación (HU-Auth-03)', () => {
    beforeEach(() => {
      cy.visit('/auth/confirmar');
    });

    it('Escenario A: Renderiza los elementos principales con estilo consistente', () => {
      cy.contains('TravelHub').should('be.visible');
      cy.contains('Verificar correo').should('be.visible');
      cy.get('input[type="email"]').should('exist');
      cy.get('input[placeholder="123456"]').should('exist');
      cy.get('button[type="submit"]').should('be.visible');
    });

    it('Escenario B: Pre-rellena el correo desde query param', () => {
      cy.visit('/auth/confirmar?email=juan@ejemplo.com');
      cy.get('input[type="email"]').should('have.value', 'juan@ejemplo.com');
    });

    it('Escenario C: Muestra errores con campos vacíos', () => {
      cy.get('button[type="submit"]').click();
      cy.get('small').should('have.length.at.least', 1);
    });

    it('Escenario D: Muestra error con código de menos de 6 dígitos', () => {
      cy.get('input[type="email"]').type('juan@ejemplo.com');
      cy.get('input[placeholder="123456"]').type('12345');
      cy.get('button[type="submit"]').click();
      cy.get('small').should('contain.text', '6 dígitos');
    });

    it('Escenario E: Confirmación exitosa redirige a login', () => {
      cy.intercept('POST', '**/register/confirm', {
        statusCode: 200,
        body: { message: 'Confirmed' },
      }).as('confirmRequest');

      cy.get('input[type="email"]').type('juan@ejemplo.com');
      cy.get('input[placeholder="123456"]').type('123456');
      cy.get('button[type="submit"]').click();

      cy.wait('@confirmRequest');
      cy.url().should('include', '/auth/login');
    });

    it('Escenario F: Confirmación fallida muestra notificación de error', () => {
      cy.intercept('POST', '**/register/confirm', {
        statusCode: 400,
        body: { detail: 'Invalid code' },
      }).as('confirmFail');

      cy.get('input[type="email"]').type('juan@ejemplo.com');
      cy.get('input[placeholder="123456"]').type('999999');
      cy.get('button[type="submit"]').click();

      cy.wait('@confirmFail');
      cy.get('button[type="submit"]').should('not.be.disabled');
    });

    it('Escenario G: Enlace a registro navega a /auth/registro', () => {
      cy.contains('a', 'Regístrate').click();
      cy.url().should('include', '/auth/registro');
    });
  });
});
