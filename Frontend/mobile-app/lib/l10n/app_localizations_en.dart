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
  String get destinationsTitle => 'Featured Destinations';

  @override
  String get viewAllText => 'See all >';

  @override
  String pricePerNight(String price) {
    return '$price US\$ / night';
  }

  @override
  String get resultsTitle => 'Search Results';

  @override
  String get specialOffer => 'Special Offer';
}
