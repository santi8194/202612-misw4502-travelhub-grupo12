const apiBaseUrl = 'http://localhost:5001';

export const environment = {
  production: false,
  apiBaseUrl,
  bookingApiUrl: `${apiBaseUrl}/booking/api/reserva`,
  catalogApiUrl: `${apiBaseUrl}/catalog`,
};
