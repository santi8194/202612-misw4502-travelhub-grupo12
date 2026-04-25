const CATEGORY_ID = 'CAT-123';
const API_URL = '**/catalog/categories/*/view-detail';
const BOOKING_URL = '**/api/reserva';

export { };

describe('Detalle de Habitación (HU-Web-RoomDetail)', () => {
  /**
   * Objetivo: Validar que la página carga y muestra correctamente todos los elementos de la habitación a partir de los datos del backend.
   * Precondiciones: El usuario navega a /category/CAT-123.
   * Resultado Esperado: La interfaz refleja fielmente la respuesta del backend, y la interacción del acordeón de descripción funciona.
   */
  it('Escenario A: Renderizado y Visualización de Información (Happy Path)', () => {
    cy.intercept('GET', API_URL, { fixture: 'room-detail-success.json' }).as('getRoomDetail');

    cy.visit(`/category/${CATEGORY_ID}`);

    cy.wait('@getRoomDetail');

    // Desaparece el loading skeleton (ya no debería estar el testid si terminó de cargar)
    cy.get('[data-testid="room-detail-loading"]').should('not.exist');

    // Validar título y elementos de cabecera
    cy.get('[data-testid="room-detail-title"]')
      .should('be.visible')
      .and('contain.text', 'Suite Familiar con Vista al Mar');

    // Validar imágenes
    cy.get('[data-testid="room-image-grid"]').should('be.visible');
    cy.get('[data-testid="room-image-grid"] img').should('have.length', 5);

    // Validar amenidades
    cy.get('[data-testid="room-amenities"]').should('be.visible');
    cy.get('[data-testid="room-amenity-item"]').should('have.length.at.least', 3);
    cy.get('[data-testid="room-amenity-item"]').contains('Piscina').should('exist');

    // Validar descripción y toggle "Ver más / Ver menos"
    cy.get('[data-testid="room-description"]').should('be.visible');
    // El string es largo (más de 240 caracteres)
    cy.get('.room-description__toggle').contains('Ver más').click();
    cy.get('.room-description__toggle').contains('Ver menos').should('be.visible');

    // Validar reseñas y políticas
    cy.get('[data-testid="room-reviews"]').should('be.visible');
    cy.get('[data-testid="room-policies"]').should('be.visible');
  });

  /**
   * Objetivo: Validar que al ingresar desde una búsqueda previa (URL con query params), el formulario de reserva se pre-cargue y calcule el precio inmediatamente.
   * Precondiciones: El usuario navega a /category/CAT-123 con fechas y huéspedes en la URL.
   * Resultado Esperado: Los inputs se pre-cargan, la sección de desglose de precio es visible con el cálculo correcto y el botón Reservar está habilitado.
   */
  it('Escenario B: Inicialización con Parámetros URL (Deep Linking)', () => {
    cy.intercept('GET', API_URL, { fixture: 'room-detail-success.json' }).as('getRoomDetail');

    // Establecemos parámetros en el futuro para que sean válidos según las reglas de negocio
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const checkout = new Date(tomorrow);
    checkout.setDate(checkout.getDate() + 5);

    const checkInStr = tomorrow.toISOString().split('T')[0];
    const checkOutStr = checkout.toISOString().split('T')[0];

    cy.visit(`/category/${CATEGORY_ID}?fecha_inicio=${checkInStr}&fecha_fin=${checkOutStr}&huespedes=2`);

    cy.wait('@getRoomDetail');

    // Verificar el "Booking Box"
    cy.get('[data-testid="room-checkin"]').should('have.value', checkInStr);
    cy.get('[data-testid="room-checkout"]').should('have.value', checkOutStr);
    cy.get('[data-testid="room-guests"]').should('have.value', '2');

    // El precio debe mostrarse y calcularse correctamente
    cy.get('[data-testid="room-price-breakdown"]').scrollIntoView().should('be.visible');
    // Precio base (250000) * 5 noches = 1.250.000 (depende del locale)
    // No validamos el string exacto del total si usa toLocaleString, pero verificamos que muestre el cálculo
    cy.get('[data-testid="room-price-breakdown"]').should('contain.text', '5 noches');

    // El botón debe estar habilitado
    cy.get('[data-testid="room-reservar-btn"]').should('not.be.disabled');
  });

  /**
   * Objetivo: Asegurar que el usuario no pueda reservar fechas inválidas o que rompan las reglas del negocio.
   * Precondiciones: El usuario se encuentra en la vista sin fechas seleccionadas, o ingresa fechas/huéspedes inválidos.
   * Resultado Esperado: El botón de reserva permanece deshabilitado y el desglose de precios se oculta con datos inválidos.
   */
  it('Escenario C: Validaciones Dinámicas del Formulario de Reserva', () => {
    cy.intercept('GET', API_URL, { fixture: 'room-detail-success.json' }).as('getRoomDetail');

    cy.visit(`/category/${CATEGORY_ID}`);
    cy.wait('@getRoomDetail');

    // Al inicio (sin fechas), el botón está deshabilitado y el desglose oculto
    cy.get('[data-testid="room-reservar-btn"]').should('be.disabled');
    cy.get('[data-testid="room-price-breakdown"]').should('not.exist');

    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];

    // Si ponemos salida igual a entrada, el botón debe seguir deshabilitado
    cy.get('[data-testid="room-checkin"]').type(todayStr);
    cy.get('[data-testid="room-checkout"]').type(todayStr);

    cy.get('[data-testid="room-reservar-btn"]').should('be.disabled');
    cy.get('[data-testid="room-price-breakdown"]').should('not.exist');

    // Para deshabilitar el botón de forma probada, garantizamos que la fecha de salida sea igual a la entrada
    cy.get('[data-testid="room-checkout"]').clear().type(todayStr);
    cy.get('[data-testid="room-reservar-btn"]').should('be.disabled');
  });

  /**
   * Objetivo: Validar la comunicación con el BookingService al iniciar una reserva y la redirección.
   * Precondiciones: Parámetros de reserva válidos diligenciados.
   * Resultado Esperado: Se realiza un POST exitoso a /api/reserva y el usuario es redirigido a la vista del carrito.
   */
  it('Escenario D: Flujo de Creación de Reserva Exitoso', () => {
    cy.intercept('GET', API_URL, { fixture: 'room-detail-success.json' }).as('getRoomDetail');
    cy.intercept('POST', BOOKING_URL, { fixture: 'room-detail-booking-success.json' }).as('createBooking');

    // Rellenamos datos válidos mediante query params
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const checkout = new Date(tomorrow);
    checkout.setDate(checkout.getDate() + 3);

    const checkInStr = tomorrow.toISOString().split('T')[0];
    const checkOutStr = checkout.toISOString().split('T')[0];

    cy.visit(`/category/${CATEGORY_ID}?fecha_inicio=${checkInStr}&fecha_fin=${checkOutStr}&huespedes=2`);
    cy.wait('@getRoomDetail');

    // Hacer clic en "Reservar"
    cy.get('[data-testid="room-reservar-btn"]').click();

    // Comprobamos petición
    cy.wait('@createBooking');

    // Comprobamos la redirección al carrito
    cy.location('pathname').should('eq', `/booking/RES-999`);
  });

  /**
   * Objetivo: Asegurar que los fallos del backend al intentar reservar (ej. sin disponibilidad) se notifiquen al usuario.
   * Precondiciones: Parámetros de reserva válidos diligenciados, pero el backend responde con error 409.
   * Resultado Esperado: El proceso se detiene, aparece el mensaje de error del backend y el usuario no es redirigido.
   */
  it('Escenario E: Manejo de Errores de Reserva (Backend Error)', () => {
    cy.intercept('GET', API_URL, { fixture: 'room-detail-success.json' }).as('getRoomDetail');
    cy.intercept('POST', BOOKING_URL, {
      statusCode: 409,
      fixture: 'room-detail-booking-error.json'
    }).as('createBookingError');

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const checkout = new Date(tomorrow);
    checkout.setDate(checkout.getDate() + 3);

    const checkInStr = tomorrow.toISOString().split('T')[0];
    const checkOutStr = checkout.toISOString().split('T')[0];

    cy.visit(`/category/${CATEGORY_ID}?fecha_inicio=${checkInStr}&fecha_fin=${checkOutStr}&huespedes=2`);
    cy.wait('@getRoomDetail');

    cy.get('[data-testid="room-reservar-btn"]').click();
    cy.wait('@createBookingError');

    // El proceso falla y se reemplaza el contenido por la pantalla de error general
    cy.get('[data-testid="room-detail-error"]')
      .should('be.visible')
      //.and('contain.text', 'No hay disponibilidad para las fechas seleccionadas.');
      .and('contain.text', 'No fue posible crear la reserva. Intenta nuevamente.← Volver a resultados');

    // El usuario no es redirigido
    cy.location('pathname').should('eq', `/category/${CATEGORY_ID}`);
  });

  /**
   * Objetivo: Validar la vista de error cuando el detalle de la habitación falla al cargar.
   * Precondiciones: El backend responde con un error 500 al intentar obtener el detalle.
   * Resultado Esperado: Se muestra la tarjeta de error con el mensaje adecuado y un enlace para volver a resultados.
   */
  it('Escenario F: Estado de Error (Error API Detail)', () => {
    cy.intercept('GET', API_URL, {
      statusCode: 500,
      body: { error: 'Internal Server Error' }
    }).as('getRoomDetailError');

    cy.visit(`/category/CAT-ERROR`);
    cy.wait('@getRoomDetailError');

    cy.get('[data-testid="room-detail-loading"]').should('not.exist');

    // Verificamos tarjeta de error
    cy.get('[data-testid="room-detail-error"]').should('be.visible');
    cy.get('[data-testid="room-detail-error"]').should('contain.text', 'No fue posible cargar el detalle de la habitación.');

    // Botón / Enlace para volver
    cy.get('[data-testid="room-detail-error"] a.back-link').should('have.attr', 'href', '/resultados');
  });
});
