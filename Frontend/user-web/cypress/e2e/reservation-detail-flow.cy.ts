const USER_ID = 'cc912e74-927e-4166-802b-3ba6a3615ebf';
const RESERVATION_ID = 'res-001';
const EMPTY_IMAGES_RESERVATION_ID = 'res-empty-images';
const UNAUTHORIZED_RESERVATION_ID = 'res-unauthorized';
const CATEGORY_ID = 'cat-001';

const hotelImage =
  'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700"%3E%3Crect width="1200" height="700" fill="%23dbeafe"/%3E%3Ctext x="600" y="350" dominant-baseline="middle" text-anchor="middle" font-size="64" fill="%231e3a8a"%3ETravelHub%3C/text%3E%3C/svg%3E';

type BookingOverride = Record<string, unknown>;

function seedAuthSession(window: Window) {
  window.localStorage.setItem('th_access_token', 'fake-access-token');
  window.localStorage.setItem('th_refresh_token', 'fake-refresh-token');
  window.localStorage.setItem('th_token_type', 'Bearer');
  window.localStorage.setItem('th_user_email', 'traveler@example.com');
  window.localStorage.setItem('th_user_id', USER_ID);
  window.localStorage.setItem('th_user_name', 'Traveler');
}

function buildBooking(overrides: BookingOverride = {}) {
  return {
    id_reserva: RESERVATION_ID,
    id_usuario: USER_ID,
    id_categoria: CATEGORY_ID,
    estado: 'CONFIRMADA',
    fecha_check_in: '2026-03-07',
    fecha_check_out: '2026-03-10',
    fecha_creacion: '2026-01-01T00:00:00Z',
    fecha_actualizacion: '2026-01-01T00:00:00Z',
    codigo_confirmacion_ota: 'TH-001',
    codigo_localizador_pms: null,
    ocupacion: { adultos: 2, ninos: 1, infantes: 0 },
    ...overrides,
  };
}

function buildCatalogDetail(images: string[] = [hotelImage]) {
  return {
    propiedad: {
      id_propiedad: 'prop-001',
      nombre: 'Hotel Central',
      estrellas: 4,
      ubicacion: {
        ciudad: 'Bogota',
        estado_provincia: 'Cundinamarca',
        pais: 'Colombia',
        coordenadas: { lat: 4.71, lng: -74.07 },
      },
      porcentaje_impuesto: '19.00',
    },
    categoria: {
      id_categoria: CATEGORY_ID,
      nombre_comercial: 'Suite Deluxe',
      descripcion: 'Habitacion amplia',
      precio_base: {
        monto: '580.00',
        moneda: 'USD',
        cargo_servicio: '0.00',
      },
      capacidad_pax: 3,
      politica_cancelacion: {
        dias_anticipacion: 3,
        porcentaje_penalidad: '50.00',
      },
    },
    amenidades: [],
    galeria: images.map((url, index) => ({
      id_media: `img-${index + 1}`,
      url_full: url,
      tipo: 'FOTO',
      orden: index + 1,
    })),
    rating_promedio: 4.8,
    total_resenas: 0,
    resenas: [],
  };
}

function mockReservationDetailApi(
  booking = buildBooking(),
  images: string[] = [hotelImage],
  reservationId = String(booking.id_reserva)
) {
  cy.intercept('GET', `**/reserva/${reservationId}`, booking).as(`getReservationDetail-${reservationId}`);
  cy.intercept('GET', `**/categories/${CATEGORY_ID}/view-detail`, buildCatalogDetail(images)).as('getCatalogDetail');
  cy.intercept('GET', `**/payments/by-reserva/${reservationId}`, {
    id_pago: 'pay-001',
    id_reserva: reservationId,
    estado: 'APPROVED',
    monto: 580,
    moneda: 'USD',
  }).as(`getPayment-${reservationId}`);
}

function mockMyReservationsApi() {
  const booking = buildBooking({ ocupacion: { adultos: 2, ninos: 0, infantes: 0 } });

  cy.intercept('GET', '**/assets/data/user-locale.json', {
    pais: 'Colombia',
    id_usuario: USER_ID,
  }).as('getLocale');

  cy.intercept('GET', `**/usuario/${USER_ID}`, [booking]).as('getBookings');

  cy.intercept('GET', `**/categories/${CATEGORY_ID}`, {
    id_categoria: CATEGORY_ID,
    nombre_comercial: 'Suite Deluxe',
    foto_portada_url: hotelImage,
  }).as('getCategory');

  cy.intercept('GET', `**/payments/by-reserva/${RESERVATION_ID}`, {
    id_pago: 'pay-001',
    id_reserva: RESERVATION_ID,
    estado: 'APPROVED',
    monto: 580,
    moneda: 'USD',
  }).as('getReservationPayment');
}

describe('Reservation Detail Flow', () => {
  it('navigates from my reservations and renders reservation detail', () => {
    mockMyReservationsApi();
    mockReservationDetailApi();

    cy.visit('/mis-reservas', {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getBookings');
    cy.get('[data-testid="btn-ver-detalles"]').first().click();

    cy.location('pathname').should('eq', `/mis-reservas/${RESERVATION_ID}`);
    cy.wait(`@getReservationDetail-${RESERVATION_ID}`);
    cy.wait('@getCatalogDetail');
    cy.wait(`@getPayment-${RESERVATION_ID}`);

    cy.get('[data-testid="reservation-detail-heading"]').should('contain.text', 'Detalles de la Reserva');
    cy.get('[data-testid="reservation-detail-current-image"]').should('be.visible');
    cy.get('[data-testid="reservation-detail-hotel"]').should('contain.text', 'Suite Deluxe');
    cy.get('[data-testid="reservation-detail-location"]').should('contain.text', 'Bogota, Colombia');
    cy.get('[data-testid="reservation-detail-check-in"]').should('contain.text', '07 mar 2026');
    cy.get('[data-testid="reservation-detail-check-out"]').should('contain.text', '10 mar 2026');
    cy.get('[data-testid="reservation-detail-guests"]').should('contain.text', '3');
    cy.get('[data-testid="reservation-detail-confirmation"]').should('contain.text', 'RES001');
    cy.get('[data-testid="reservation-detail-total"]').should('contain.text', '580').and('contain.text', 'US$');
    cy.get('[data-testid="reservation-detail-status"]').should('contain.text', 'Confirmada');
    cy.get('[data-testid="reservation-detail-cancel"]').should('be.visible');
  });

  it('renders fallback image when catalog has no images', () => {
    mockReservationDetailApi(
      buildBooking({ id_reserva: EMPTY_IMAGES_RESERVATION_ID }),
      [],
      EMPTY_IMAGES_RESERVATION_ID
    );

    cy.visit(`/mis-reservas/${EMPTY_IMAGES_RESERVATION_ID}`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait(`@getReservationDetail-${EMPTY_IMAGES_RESERVATION_ID}`);
    cy.wait('@getCatalogDetail');

    cy.get('[data-testid="reservation-detail-image-fallback"]').should('be.visible');
    cy.get('[data-testid="gallery-next"]').should('not.exist');
    cy.get('[data-testid="reservation-detail-hotel"]').should('contain.text', 'Suite Deluxe');
  });

  it('does not render sensitive detail when reservation belongs to another user', () => {
    cy.intercept('GET', `**/reserva/${UNAUTHORIZED_RESERVATION_ID}`, buildBooking({
      id_reserva: UNAUTHORIZED_RESERVATION_ID,
      id_usuario: 'other-user',
    })).as('getUnauthorizedReservation');

    cy.visit(`/mis-reservas/${UNAUTHORIZED_RESERVATION_ID}`, {
      onBeforeLoad(window) {
        window.localStorage.clear();
        seedAuthSession(window);
      },
    });

    cy.wait('@getUnauthorizedReservation');

    cy.get('[data-testid="reservation-detail-unauthorized"]').should('be.visible');
    cy.get('[data-testid="reservation-detail-unauthorized"]').should('contain.text', 'Reserva no disponible');
    cy.get('[data-testid="reservation-detail-success"]').should('not.exist');
    cy.contains('Suite Deluxe').should('not.exist');
  });
});
