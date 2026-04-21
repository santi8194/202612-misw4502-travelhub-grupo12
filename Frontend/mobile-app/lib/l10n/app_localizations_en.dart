// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get loginTitle => 'Login';

  @override
  String get emailLabel => 'Email address';

  @override
  String get passwordLabel => 'Password';

  @override
  String get loginButton => 'Enter';

  @override
  String get noAccountText => 'Don\'t have an account? ';

  @override
  String get registerLink => 'Register';

  @override
  String get registerTitle => 'Registration';

  @override
  String get fullNameLabel => 'Full Name';

  @override
  String get confirmPasswordLabel => 'Confirm Password';

  @override
  String get registerButton => 'Register';

  @override
  String get haveAccountText => 'Already have an account? ';

  @override
  String get loginLink => 'Login';

  @override
  String get navHome => 'Home';

  @override
  String get navSearch => 'Search';

  @override
  String get navBookings => 'Bookings';

  @override
  String get navProfile => 'Profile';

  @override
  String get homeTitle => 'Home Screen';

  @override
  String get searchTitle => 'Search Screen';

  @override
  String get bookingsTitle => 'Bookings Screen';

  @override
  String get profileTitle => 'Profile Screen';

  @override
  String get headerSubtitle =>
      'Discover your next destination in Latin America';

  @override
  String get searchWhere => 'Where do you want to go?';

  @override
  String get searchDates => 'DATES';

  @override
  String get searchGuests => 'GUESTS';

  @override
  String get searchButton => 'Search Hotels';

  @override
  String get resultsTitle => 'Search Results';

  @override
  String get confirmReservationTitle => 'Confirm Reservation';

  @override
  String get reservationDetailsTitle => 'Reservation Details';

  @override
  String get reservationDatesLabel => 'Dates';

  @override
  String get reservationGuestsLabel => 'Guests';

  @override
  String get reservationReferenceLabel => 'Reservation ID';

  @override
  String get confirmReservationButton => 'Confirm Reservation';

  @override
  String get reservationSuccessMessage =>
      'Your reservation has been confirmed successfully.';

  @override
  String get specialOffer => 'Special Offer';

  @override
  String get noResultsTitle => 'No properties available';

  @override
  String get noResultsMessage =>
      'No properties were found matching your search. Try adjusting your destination, dates, or number of guests.';

  @override
  String guestCountLabel(int count) {
    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$count guests',
      one: '1 guest',
    );
    return '$_temp0';
  }

  @override
  String get searchingButton => 'Searching...';

  @override
  String get anyDestination => 'ANY DESTINATION';

  @override
  String get openDates => 'OPEN DATES';

  @override
  String get tryAnotherSearch => 'Try another search';

  @override
  String get cachedResultsBanner =>
      'Showing cached results. They will be updated once connection is restored.';

  @override
  String currencyBubbleLabel(String currency) {
    return 'CURRENCY: $currency';
  }

  @override
  String get currencyCodeUSD => 'USD';

  @override
  String get currencyCodeCOP => 'COP';

  @override
  String get taxesAndCharges => 'Taxes and charges';

  @override
  String get totalPrice => 'Total';

  @override
  String get paymentMethod => 'Payment Method';

  @override
  String get cardEnding => 'Visa ending in •••• 4242';

  @override
  String get tripDetailsTitle => 'TRIP DETAILS';

  @override
  String get priceBreakdownTitle => 'PRICE BREAKDOWN';
}
