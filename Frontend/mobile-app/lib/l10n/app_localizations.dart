import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_es.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('es'),
  ];

  /// No description provided for @loginTitle.
  ///
  /// In en, this message translates to:
  /// **'Login'**
  String get loginTitle;

  /// No description provided for @emailLabel.
  ///
  /// In en, this message translates to:
  /// **'Email address'**
  String get emailLabel;

  /// No description provided for @passwordLabel.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get passwordLabel;

  /// No description provided for @loginButton.
  ///
  /// In en, this message translates to:
  /// **'Enter'**
  String get loginButton;

  /// No description provided for @noAccountText.
  ///
  /// In en, this message translates to:
  /// **'Don\'t have an account? '**
  String get noAccountText;

  /// No description provided for @registerLink.
  ///
  /// In en, this message translates to:
  /// **'Register'**
  String get registerLink;

  /// No description provided for @registerTitle.
  ///
  /// In en, this message translates to:
  /// **'Registration'**
  String get registerTitle;

  /// No description provided for @fullNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Full Name'**
  String get fullNameLabel;

  /// No description provided for @confirmPasswordLabel.
  ///
  /// In en, this message translates to:
  /// **'Confirm Password'**
  String get confirmPasswordLabel;

  /// No description provided for @registerButton.
  ///
  /// In en, this message translates to:
  /// **'Register'**
  String get registerButton;

  /// No description provided for @haveAccountText.
  ///
  /// In en, this message translates to:
  /// **'Already have an account? '**
  String get haveAccountText;

  /// No description provided for @loginLink.
  ///
  /// In en, this message translates to:
  /// **'Login'**
  String get loginLink;

  /// No description provided for @navHome.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get navHome;

  /// No description provided for @navSearch.
  ///
  /// In en, this message translates to:
  /// **'Search'**
  String get navSearch;

  /// No description provided for @navBookings.
  ///
  /// In en, this message translates to:
  /// **'Bookings'**
  String get navBookings;

  /// No description provided for @navProfile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get navProfile;

  /// No description provided for @homeTitle.
  ///
  /// In en, this message translates to:
  /// **'Home Screen'**
  String get homeTitle;

  /// No description provided for @searchTitle.
  ///
  /// In en, this message translates to:
  /// **'Search Screen'**
  String get searchTitle;

  /// No description provided for @bookingsTitle.
  ///
  /// In en, this message translates to:
  /// **'Bookings Screen'**
  String get bookingsTitle;

  /// No description provided for @profileTitle.
  ///
  /// In en, this message translates to:
  /// **'Profile Screen'**
  String get profileTitle;

  /// No description provided for @headerSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Discover your next destination in Latin America'**
  String get headerSubtitle;

  /// No description provided for @searchWhere.
  ///
  /// In en, this message translates to:
  /// **'Where do you want to go?'**
  String get searchWhere;

  /// No description provided for @searchDates.
  ///
  /// In en, this message translates to:
  /// **'DATES'**
  String get searchDates;

  /// No description provided for @searchGuests.
  ///
  /// In en, this message translates to:
  /// **'GUESTS'**
  String get searchGuests;

  /// No description provided for @searchButton.
  ///
  /// In en, this message translates to:
  /// **'Search Hotels'**
  String get searchButton;

  /// No description provided for @resultsTitle.
  ///
  /// In en, this message translates to:
  /// **'Search Results'**
  String get resultsTitle;

  /// No description provided for @confirmReservationTitle.
  ///
  /// In en, this message translates to:
  /// **'Confirm Reservation'**
  String get confirmReservationTitle;

  /// No description provided for @reservationDetailsTitle.
  ///
  /// In en, this message translates to:
  /// **'Reservation Details'**
  String get reservationDetailsTitle;

  /// No description provided for @reservationDatesLabel.
  ///
  /// In en, this message translates to:
  /// **'Dates'**
  String get reservationDatesLabel;

  /// No description provided for @reservationGuestsLabel.
  ///
  /// In en, this message translates to:
  /// **'Guests'**
  String get reservationGuestsLabel;

  /// No description provided for @reservationReferenceLabel.
  ///
  /// In en, this message translates to:
  /// **'Reservation ID'**
  String get reservationReferenceLabel;

  /// No description provided for @confirmReservationButton.
  ///
  /// In en, this message translates to:
  /// **'Confirm Reservation'**
  String get confirmReservationButton;

  /// No description provided for @reservationSuccessMessage.
  ///
  /// In en, this message translates to:
  /// **'Your reservation has been confirmed successfully.'**
  String get reservationSuccessMessage;

  /// No description provided for @specialOffer.
  ///
  /// In en, this message translates to:
  /// **'Special Offer'**
  String get specialOffer;

  /// No description provided for @noResultsTitle.
  ///
  /// In en, this message translates to:
  /// **'No properties available'**
  String get noResultsTitle;

  /// No description provided for @noResultsMessage.
  ///
  /// In en, this message translates to:
  /// **'No properties were found matching your search. Try adjusting your destination, dates, or number of guests.'**
  String get noResultsMessage;

  /// No description provided for @guestCountLabel.
  ///
  /// In en, this message translates to:
  /// **'{count, plural, =1{1 guest} other{{count} guests}}'**
  String guestCountLabel(int count);

  /// No description provided for @searchingButton.
  ///
  /// In en, this message translates to:
  /// **'Searching...'**
  String get searchingButton;

  /// No description provided for @anyDestination.
  ///
  /// In en, this message translates to:
  /// **'ANY DESTINATION'**
  String get anyDestination;

  /// No description provided for @openDates.
  ///
  /// In en, this message translates to:
  /// **'OPEN DATES'**
  String get openDates;

  /// No description provided for @tryAnotherSearch.
  ///
  /// In en, this message translates to:
  /// **'Try another search'**
  String get tryAnotherSearch;

  /// No description provided for @cachedResultsBanner.
  ///
  /// In en, this message translates to:
  /// **'Showing cached results. They will be updated once connection is restored.'**
  String get cachedResultsBanner;

  /// No description provided for @currencyBubbleLabel.
  ///
  /// In en, this message translates to:
  /// **'CURRENCY: {currency}'**
  String currencyBubbleLabel(String currency);

  /// No description provided for @currencyCodeUSD.
  ///
  /// In en, this message translates to:
  /// **'USD'**
  String get currencyCodeUSD;

  /// No description provided for @currencyCodeCOP.
  ///
  /// In en, this message translates to:
  /// **'COP'**
  String get currencyCodeCOP;

  /// No description provided for @taxesAndCharges.
  ///
  /// In en, this message translates to:
  /// **'Taxes and charges'**
  String get taxesAndCharges;

  /// No description provided for @totalPrice.
  ///
  /// In en, this message translates to:
  /// **'Total'**
  String get totalPrice;

  /// No description provided for @paymentMethod.
  ///
  /// In en, this message translates to:
  /// **'Payment Method'**
  String get paymentMethod;

  /// No description provided for @cardEnding.
  ///
  /// In en, this message translates to:
  /// **'Visa ending in •••• 4242'**
  String get cardEnding;

  /// No description provided for @tripDetailsTitle.
  ///
  /// In en, this message translates to:
  /// **'TRIP DETAILS'**
  String get tripDetailsTitle;

  /// No description provided for @priceBreakdownTitle.
  ///
  /// In en, this message translates to:
  /// **'PRICE BREAKDOWN'**
  String get priceBreakdownTitle;

  /// No description provided for @profileVersion.
  ///
  /// In en, this message translates to:
  /// **'Version: {version}'**
  String profileVersion(String version);

  /// No description provided for @nightsLabel.
  ///
  /// In en, this message translates to:
  /// **'{count, plural, =1{1 night} other{{count} nights}}'**
  String nightsLabel(int count);

  /// No description provided for @profileTitleView.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get profileTitleView;

  /// No description provided for @countryLabel.
  ///
  /// In en, this message translates to:
  /// **'Country'**
  String get countryLabel;

  /// No description provided for @countryNotSet.
  ///
  /// In en, this message translates to:
  /// **'Not set'**
  String get countryNotSet;

  /// No description provided for @propertyInfoTab.
  ///
  /// In en, this message translates to:
  /// **'Information'**
  String get propertyInfoTab;

  /// No description provided for @propertyRoomsTab.
  ///
  /// In en, this message translates to:
  /// **'Rooms'**
  String get propertyRoomsTab;

  /// No description provided for @aboutProperty.
  ///
  /// In en, this message translates to:
  /// **'About the property'**
  String get aboutProperty;

  /// No description provided for @mainAmenities.
  ///
  /// In en, this message translates to:
  /// **'Main amenities'**
  String get mainAmenities;

  /// No description provided for @roomGallery.
  ///
  /// In en, this message translates to:
  /// **'Room Gallery'**
  String get roomGallery;

  /// No description provided for @reserveNow.
  ///
  /// In en, this message translates to:
  /// **'Book Now'**
  String get reserveNow;

  /// No description provided for @totalPriceLabel.
  ///
  /// In en, this message translates to:
  /// **'TOTAL PRICE'**
  String get totalPriceLabel;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'es'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'es':
      return AppLocalizationsEs();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
