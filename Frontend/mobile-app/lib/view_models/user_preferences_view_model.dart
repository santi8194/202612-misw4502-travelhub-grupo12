import 'package:flutter/material.dart';

class UserPreferencesViewModel extends ChangeNotifier {
  String? _country;

  String? get country => _country;

  void setCountry(String? value) {
    if (_country == value) return;
    _country = value;
    notifyListeners();
  }
}
