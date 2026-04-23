import 'dart:convert';

import 'package:flutter/services.dart';

import '../models/country_tax.dart';

class TaxConfigService {
  static Future<Map<String, CountryTax>> load() async {
    final raw = await rootBundle.loadString('assets/data/country_taxes.json');
    final Map<String, dynamic> json = jsonDecode(raw) as Map<String, dynamic>;
    return json.map(
      (key, value) =>
          MapEntry(key, CountryTax.fromJson(value as Map<String, dynamic>)),
    );
  }
}
