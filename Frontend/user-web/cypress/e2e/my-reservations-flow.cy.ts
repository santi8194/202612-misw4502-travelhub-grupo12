describe('My Reservations Flow', () => {
  const BOOKING_URL = 'http://localhost:5001/booking/api/reserva';
  const CATALOG_URL = 'http://localhost:5001/catalog';
  const PAYMENT_URL = 'http://localhost:5001/payment';

  beforeEach(() => {
    cy.fixture('my-reservations-mock.json').then((mockData) => {
      // Intercept locale
      cy.intercept('GET', '**/assets/data/user-locale.json', mockData.locale).as('getLocale');

      // Intercept Booking
      cy.intercept('GET', `${BOOKING_URL}/usuario/${mockData.locale.id_usuario}`, mockData.bookings).as('getBookings');

      // Intercept Catalog Categories
      cy.intercept('GET', `${CATALOG_URL}/categories/*`, (req) => {
        const id = req.url.split('/').pop();
        if (id && mockData.categories[id]) {
          req.reply(mockData.categories[id]);
        } else {
          req.reply(404, {});
        }
      }).as('getCategory');

      // Intercept Payment
      cy.intercept('GET', `${PAYMENT_URL}/payments/by-reserva/*`, (req) => {
        const id = req.url.split('/').pop();
        if (id && mockData.payments[id]) {
          req.reply(mockData.payments[id]);
        } else {
          req.reply([]);
        }
      }).as('getPayments');

      // Intercept Calculate Price
      cy.intercept('POST', `${CATALOG_URL}/calculate-room-price`, mockData.priceFallback).as('calculatePrice');
    });
  });

  describe('Scenario 1: Initial Render and Happy Path', () => {
    it('should fetch data and render all reservation cards correctly', () => {
      cy.visit('/mis-reservas');

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
        cy.get('[data-testid="reservation-price"]').should('contain.text', '$580');
        cy.get('[data-testid="reservation-confirmation"]').should('contain.text', 'TH-001');
      });
    });
  });

  describe('Scenario 2: Navigation and Filters', () => {
    it('should filter cards based on the selected status', () => {
      cy.visit('/mis-reservas');
      cy.wait('@getBookings');

      // Filter: Confirmadas
      cy.get('[data-testid="filter-confirmadas"]').click();
      cy.get('[data-testid="reservation-card"]').should('have.length', 1);
      cy.get('[data-testid="reservation-status-badge"]').should('contain.text', 'Confirmada');

      // Filter: Pendientes
      cy.get('[data-testid="filter-pendientes"]').click();
      cy.get('[data-testid="reservation-card"]').should('have.length', 1);
      cy.get('[data-testid="reservation-status-badge"]').should('contain.text', 'Pendiente Confirmación');
      // Should show the "Cancelar Reserva" button (PENDIENTE_CONFIRMACION_HOTEL)
      cy.get('[data-testid="btn-cancelar-reserva"]').should('exist').and('be.visible');

      // Filter: Todas
      cy.get('[data-testid="filter-todas"]').click();
      cy.get('[data-testid="reservation-card"]').should('have.length', 3);
    });

    it('should show empty state when filtering a status with no reservations', () => {
      // Change the mock to have no CANCELADA reservations dynamically
      cy.fixture('my-reservations-mock.json').then((mockData) => {
        const noCancelledBookings = mockData.bookings.filter((b: any) => b.estado !== 'CANCELADA');
        cy.intercept('GET', `${BOOKING_URL}/usuario/${mockData.locale.id_usuario}`, noCancelledBookings).as('getBookingsEmptyCancel');
      });

      cy.visit('/mis-reservas');
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
      cy.visit('/mis-reservas');
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
        cy.get('[data-testid="reservation-price"]').should('contain.text', 'COP').and('contain.text', '1,500');
      });
    });
  });

  describe('Scenario 4: Critical Error Handling (Booking 500)', () => {
    it('should handle API failure gracefully and show empty state without crashing', () => {
      cy.fixture('my-reservations-mock.json').then((mockData) => {
        // Force a 500 error on the main Booking API call
        cy.intercept('GET', `${BOOKING_URL}/usuario/${mockData.locale.id_usuario}`, {
          statusCode: 500,
          body: { error: 'Internal Server Error' }
        }).as('getBookings500');
      });

      cy.visit('/mis-reservas');
      cy.wait('@getBookings500');

      // The page should survive: counters at 0 and empty state visible
      cy.get('[data-testid="count-total"]').should('contain.text', '0');
      cy.get('[data-testid="reservation-card"]').should('not.exist');
      cy.get('[data-testid="empty-state"]').should('be.visible');
    });
  });
});
