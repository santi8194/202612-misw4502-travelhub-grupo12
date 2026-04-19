// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Spanish Castilian (`es`).
class AppLocalizationsEs extends AppLocalizations {
  AppLocalizationsEs([String locale = 'es']) : super(locale);

  @override
  String get loginTitle => 'Iniciar sesión';

  @override
  String get emailLabel => 'Correo electrónico';

  @override
  String get passwordLabel => 'Contraseña';

  @override
  String get loginButton => 'Ingresar';

  @override
  String get noAccountText => '¿No tienes una cuenta? ';

  @override
  String get registerLink => 'Regístrate';

  @override
  String get registerTitle => 'Registro';

  @override
  String get fullNameLabel => 'Nombre completo';

  @override
  String get confirmPasswordLabel => 'Confirmar contraseña';

  @override
  String get registerButton => 'Registrarse';

  @override
  String get haveAccountText => '¿Ya tienes una cuenta? ';

  @override
  String get loginLink => 'Inicia sesión';

  @override
  String get navHome => 'Inicio';

  @override
  String get navSearch => 'Buscar';

  @override
  String get navBookings => 'Reservas';

  @override
  String get navProfile => 'Perfil';

  @override
  String get homeTitle => 'Pantalla de Inicio';

  @override
  String get searchTitle => 'Pantalla de Búsqueda';

  @override
  String get bookingsTitle => 'Pantalla de Reservas';

  @override
  String get profileTitle => 'Pantalla de Perfil';

  @override
  String get headerSubtitle => 'Descubre tu próximo destino en América Latina';

  @override
  String get searchWhere => '¿A dónde quieres ir?';

  @override
  String get searchDates => 'FECHAS';

  @override
  String get searchGuests => 'HUÉSPEDES';

  @override
  String get searchButton => 'Buscar Hoteles';

  @override
  String get resultsTitle => 'Resultados de búsqueda';

  @override
  String get confirmReservationTitle => 'Confirmar reserva';

  @override
  String get reservationDetailsTitle => 'Detalles de la reserva';

  @override
  String get reservationDatesLabel => 'Fechas';

  @override
  String get reservationGuestsLabel => 'Huéspedes';

  @override
  String get reservationReferenceLabel => 'ID de reserva';

  @override
  String get confirmReservationButton => 'Confirmar reserva';

  @override
  String get reservationSuccessMessage =>
      'Tu reserva ha sido confirmada con éxito.';

  @override
  String get specialOffer => 'Oferta Especial';

  @override
  String get noResultsTitle => 'No hay propiedades disponibles';

  @override
  String get noResultsMessage =>
      'No se encontraron propiedades que coincidan con tu búsqueda. Intenta ajustar el destino, las fechas o la cantidad de huéspedes.';

  @override
  String guestCountLabel(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count huéspedes',
      one: '1 huésped',
    );
    return '$_temp0';
  }

  @override
  String get searchingButton => 'Buscando...';

  @override
  String get anyDestination => 'CUALQUIER DESTINO';

  @override
  String get openDates => 'FECHAS ABIERTAS';

  @override
  String get tryAnotherSearch => 'Intentar otra búsqueda';

  @override
  String get cachedResultsBanner =>
      'Mostrando resultados en caché. Se actualizarán al recuperar conexión.';

  @override
  String currencyBubbleLabel(String currency) {
    return 'MONEDA: $currency';
  }

  @override
  String get currencyCodeUSD => 'USD';

  @override
  String get currencyCodeCOP => 'COP';
}
