import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

class UserPreferencesViewModel extends ChangeNotifier {
  String? _country;

  UserPreferencesViewModel({String? languageCode}) {
    final lang =
        languageCode ??
        WidgetsBinding.instance.platformDispatcher.locale.languageCode;
    _country = _defaultCountryForLanguage(lang);
  }

  String? get country => _country;

  static String _defaultCountryForLanguage(String languageCode) {
    return languageCode == 'es' ? 'Colombia' : 'USA';
  }

  void setCountry(String? value) {
    if (_country == value) return;
    _country = value;
    notifyListeners();
  }
}
