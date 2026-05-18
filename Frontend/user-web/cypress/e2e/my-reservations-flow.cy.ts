describe('My Reservations Flow', () => {
  const USER_ID = 'cc912e74-927e-4166-802b-3ba6a3615ebf';

  function visitMyReservations() {
    cy.visit('/mis-reservas', {
      onBeforeLoad(window) {
        window.localStorage.setItem('th_access_token', 'fake-access-token');
        window.localStorage.setItem('th_refresh_token', 'fake-refresh-token');
        window.localStorage.setItem('th_token_type', 'Bearer');
        window.localStorage.setItem('th_user_email', 'traveler@example.com');
        window.localStorage.setItem('th_user_id', USER_ID);
        window.localStorage.setItem('th_user_name', 'Traveler');
      },
    });
  }

  // Los interceptores usan comodines (**) para ser agnósticos del environment.
  // Así funcionan sin importar si environment.ts apunta a localhost o a una IP.

  beforeEach(() => {
    cy.fixture('my-reservations-mock.json').then((mockData) => {
      // Intercept locale
      cy.intercept('GET', '**/assets/data/user-locale.json', mockData.locale).as('getLocale');

      // Intercept Booking
      cy.intercept('GET', `**/usuario/${mockData.locale.id_usuario}`, mockData.bookings).as('getBookings');

      // Intercept User Profile
      cy.intercept('GET', `**/users/${mockData.locale.id_usuario}`, {
        id_usuario: mockData.locale.id_usuario,
        nombre_completo: 'Test User',
        first_name: 'Test',
        last_name: 'User',
        email: 'test@example.com',
        username: 'test.user'
      }).as('getUserProfile');

      // Intercept Catalog Categories
      cy.intercept('GET', `**/categories/*`, (req) => {
        const id = req.url.split('/').pop();
        if (id && mockData.categories[id]) {
          req.reply(mockData.categories[id]);
        } else {
          req.reply(404, {});
        }
      }).as('getCategory');

      // Intercept Payment
      cy.intercept('GET', `**/payments/by-reserva/*`, (req) => {
        const id = req.url.split('/').pop();
        if (id && mockData.payments[id]) {
          req.reply(mockData.payments[id]);
        } else {
          req.reply(404, { detail: 'Pago no encontrado para la reserva' });
        }
      }).as('getPayments');

      // Intercept Calculate Price
      cy.intercept('POST', `**/calculate-room-price`, mockData.priceFallback).as('calculatePrice');
    });
  });

  describe('Scenario 1: Initial Render and Happy Path', () => {
    it('should fetch data and render all reservation cards correctly', () => {
      visitMyReservations();

      cy.wait('@getLocale');
      cy.wait('@getBookings');

      // Validate Counters
      cy.get('[data-testid="count-total"]').should('contain.text', '3');
      cy.get('[data-testid="count-confirmadas"]').should('contain.text', '1');
      cy.get('[data-testid="count-pendientes"]').should('contain.text', '1');
      cy.get('[data-testid="count-canceladas"]').should('contain.text', '1');

      // Validate Cards
      cy.get('[data-testid="reservations-list"]')
        .find('[data-testid="reservation-card"]')
        .should('have.length', 3);

      // Validate specific card data (First card - CONFIRMADA)
      cy.get('[data-testid="reservation-card"]').eq(0).within(() => {
        cy.get('[data-testid="reservation-name"]').should('contain.text', 'Suite Deluxe');
        cy.get('[data-testid="reservation-status-badge"]').should('contain.text', 'Confirmada');
        cy.get('[data-testid="reservation-price"]').should('contain.text', '580').and('contain.text', 'US$');
        cy.get('[data-testid="reservation-id"]')
          .should('contain.text', 'Código confirmación')
          .and('contain.text', 'RES001');
        cy.get('[data-testid="reservation-confirmation"]').should('not.exist');
      });
    });
  });

  describe('Scenario 2: Navigation and Filters', () => {
    it('should filter cards based on the selected status', () => {
      visitMyReservations();
      cy.wait('@getBookings');

      // Filter: Confirmadas
      cy.get('[data-testid="filter-confirmadas"]').click();
      cy.get('[data-testid="reservation-card"]').should('have.length', 1);
      cy.get('[data-testid="reservation-status-badge"]').should('contain.text', 'Confirmada');

      // Filter: Pendientes
      cy.get('[data-testid="filter-pendientes"]').click();
      cy.get('[data-testid="reservation-card"]').should('have.length', 1);
      cy.get('[data-testid="reservation-status-badge"]').should('contain.text', 'Pendiente por confirmación');
      // Cancellation starts from reservation detail, not directly from the card.
      cy.get('[data-testid="btn-cancelar-reserva"]').should('not.exist');

      // Filter: Todas
      cy.get('[data-testid="filter-todas"]').click();
      cy.get('[data-testid="reservation-card"]').should('have.length', 3);
    });

    it('should show empty state when filtering a status with no reservations', () => {
      // Change the mock to have no CANCELADA reservations dynamically
      cy.fixture('my-reservations-mock.json').then((mockData) => {
        const noCancelledBookings = mockData.bookings.filter((b: any) => b.estado !== 'CANCELADA');
        cy.intercept('GET', `**/usuario/${mockData.locale.id_usuario}`, noCancelledBookings).as('getBookingsEmptyCancel');
      });

      visitMyReservations();
      cy.wait('@getBookingsEmptyCancel');

      // Check counter is 0
      cy.get('[data-testid="count-canceladas"]').should('contain.text', '0');

      // Filter Canceladas
      cy.get('[data-testid="filter-canceladas"]').click();

      // Should show empty state and no cards
      cy.get('[data-testid="reservation-card"]').should('not.exist');
      cy.get('[data-testid="empty-state"]').should('be.visible');
    });
  });

  describe('Scenario 3: Price Fallback (Payment 404/Empty)', () => {
    it('should fetch and display calculated price from catalog when payment is not available', () => {
      // The 3rd reservation (res-003, CANCELADA) has no payments in the mock.
      visitMyReservations();
      cy.wait('@getBookings');

      // Wait for calculatePrice fallback call
      cy.wait('@calculatePrice').then((interception) => {
        // Assert the body of the POST request
        expect(interception.request.body).to.deep.equal({
          id_categoria: "cat-003",
          fecha_inicio: "2026-02-09",
          fecha_fin: "2026-02-12",
          pais_usuario: "Colombia"
        });
      });

      // Filter Canceladas to see res-003 easily
      cy.get('[data-testid="filter-canceladas"]').click();

      // Validate that it shows the price from calculate-room-price (COP 1,500)
      cy.get('[data-testid="reservation-card"]').within(() => {
        cy.get('[data-testid="reservation-price"]').should('contain.text', '1500').and('contain.text', 'COP');
      });
    });
  });

  describe('Scenario 4: Critical Error Handling (Booking 500)', () => {
    it('should handle API failure gracefully and show empty state without crashing', () => {
      cy.fixture('my-reservations-mock.json').then((mockData) => {
        // Force a 500 error on the main Booking API call
        cy.intercept('GET', `**/usuario/${mockData.locale.id_usuario}`, {
          statusCode: 500,
          body: { error: 'Internal Server Error' }
        }).as('getBookings500');
      });

      visitMyReservations();
      cy.wait('@getBookings500');

      // The page should survive: counters at 0 and empty state visible
      cy.get('[data-testid="count-total"]').should('contain.text', '0');
      cy.get('[data-testid="reservation-card"]').should('not.exist');
      cy.get('[data-testid="empty-state"]').should('be.visible');
    });
  });
});
