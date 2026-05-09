describe('Header Profile Display with User API', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Authenticated User Profile Display', () => {
    beforeEach(() => {
      // Set up authenticated session
      cy.window().then((window) => {
        window.localStorage.setItem('th_access_token', 'fake-access-token-header-test');
        window.localStorage.setItem('th_refresh_token', 'fake-refresh-token');
        window.localStorage.setItem('th_token_type', 'Bearer');
        window.localStorage.setItem('th_user_email', 'mariana@travelhub.com');
        window.localStorage.setItem('th_user_id', 'user-mariana-001');
        window.localStorage.setItem('th_user_name', 'm.diaza2');
      });

      // Mock the user profile endpoint
      cy.intercept('GET', '**/users/user-mariana-001', {
        statusCode: 200,
        body: {
          id_usuario: 'user-mariana-001',
          full_name: 'Mariana Diaz Aguirre',
          email: 'mariana@travelhub.com',
          rol: 'traveler'
        }
      }).as('getUserProfile');
    });

    it('should display full name from user profile in header menu', () => {
      cy.visit('/');
      
      // Open profile menu
      cy.get('[aria-label="Abrir menú de perfil"]').click();

      // Wait for user profile API call
      cy.wait('@getUserProfile');

      // Verify the full name (nombre_completo) is displayed
      cy.get('.profile-name').should('contain.text', 'Mariana Diaz Aguirre');
    });

    it('should display fallback username when full_name is not available in profile', () => {
      cy.intercept('GET', '**/users/user-mariana-001', {
        statusCode: 200,
        body: {
          id_usuario: 'user-mariana-001',
          email: 'mariana@travelhub.com'
          // No full_name field
        }
      }).as('getUserProfileAlt');

      cy.visit('/');
      
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.wait('@getUserProfileAlt');

      // Should display the fallback username from localStorage (th_user_name)
      cy.get('.profile-name').should('contain.text', 'm.diaza2');
    });

    it('should display fallback name when user profile endpoint fails', () => {
      cy.intercept('GET', '**/users/user-mariana-001', {
        statusCode: 500,
        body: { error: 'Server error' }
      }).as('getUserProfileError');

      cy.visit('/');
      
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.wait('@getUserProfileError');

      // Should display the fallback name from JWT (username)
      cy.get('.profile-name').should('contain.text', 'm.diaza2');
    });

    it('should cache user profile and not call API again on subsequent menu opens', () => {
      cy.visit('/');
      
      // First open
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.wait('@getUserProfile');
      cy.get('.profile-name').should('contain.text', 'Mariana Diaz Aguirre');

      // Close menu
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.get('.profile-dropdown').should('not.exist');

      // Second open - should use cached data, not call API again
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      
      // Verify only one API call was made
      cy.get('@getUserProfile.all').then((calls) => {
        expect(calls).to.have.lengthOf(1);
      });

      cy.get('.profile-name').should('contain.text', 'Mariana Diaz Aguirre');
    });

    it('should display menu items with user profile open', () => {
      cy.visit('/');
      
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.wait('@getUserProfile');

      cy.get('.profile-dropdown').should('be.visible');
      cy.get('.dropdown-item--button').should('contain.text', 'Mis Reservas');
      cy.get('.dropdown-item--button').should('contain.text', 'Cerrar sesión');
    });

    it('should close menu when clicking outside', () => {
      cy.visit('/');
      
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.wait('@getUserProfile');
      cy.get('.profile-dropdown').should('be.visible');

      cy.get('html').click('bottomRight', { force: true });
      cy.get('.profile-dropdown').should('not.exist');
    });

    it('should show success notification when user logs out and clear booking state', () => {
      cy.visit('/');
      
      // Set booking session before logout
      cy.window().then((window) => {
        window.sessionStorage.setItem('booking-session:test-sig', JSON.stringify({
          expiresAt: Date.now() + 900000
        }));
        window.sessionStorage.setItem('hold:reservation-id', JSON.stringify({
          holdId: 'test-hold'
        }));
      });
      
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.wait('@getUserProfile');

      // Find and click logout button
      cy.get('.profile-dropdown')
        .find('.dropdown-item--button')
        .contains('Cerrar sesión')
        .click();

      // Should see success notification
      cy.get('.notification-toast').should('contain.text', 'Tu sesión ha sido cerrada exitosamente');
      cy.get('.notification-toast').click();
      cy.get('.notification-toast').should('not.exist');

      // Verify booking sessions were cleared from sessionStorage
      cy.window().then((window) => {
        expect(window.sessionStorage.getItem('booking-session:test-sig')).to.be.null;
        expect(window.sessionStorage.getItem('hold:reservation-id')).to.be.null;
      });

      // Profile menu should close
      cy.get('.profile-dropdown').should('not.exist');

      // Session should be cleared (profile button should no longer show authenticated state)
      cy.get('[aria-label="Abrir menú de perfil"]').click();
      cy.get('.profile-dropdown').should('be.visible');
      cy.get('.profile-dropdown').should('contain.text', 'Registrarse');
      cy.get('.profile-dropdown').should('contain.text', 'Iniciar Sesión');
    });
  });

  describe('Unauthenticated User', () => {
    it('should show login and register options when not authenticated', () => {
      cy.visit('/');
      
      cy.get('[aria-label="Abrir menú de perfil"]').click();

      cy.get('.profile-dropdown').should('be.visible');
      cy.contains('Registrarse').should('be.visible');
      cy.contains('Iniciar Sesión').should('be.visible');
    });
  });
});
