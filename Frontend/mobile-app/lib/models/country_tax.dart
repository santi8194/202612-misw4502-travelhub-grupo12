class TaxInfo {
  final String name;
  final double rate;
  final Map<String, String> note;

  const TaxInfo({required this.name, required this.rate, required this.note});

  String noteForLanguage(String languageCode) {
    return note[languageCode] ?? note['en'] ?? note['es'] ?? '';
  }

  factory TaxInfo.fromJson(Map<String, dynamic> json) {
    final rawNote = json['note'];
    final parsedNote = switch (rawNote) {
      String value => {'es': value, 'en': value},
      Map<String, dynamic> value => value.map(
        (key, value) => MapEntry(key, value as String),
      ),
      _ => const <String, String>{'es': '', 'en': ''},
    };

    return TaxInfo(
      name: json['name'] as String,
      rate: (json['rate'] as num).toDouble(),
      note: parsedNote,
    );
  }
}

class CountryTax {
  final String currency;
  final String currencySymbol;
  final String locale;
  final int decimals;
  final double usdRate;
  final TaxInfo tax;

  const CountryTax({
    required this.currency,
    required this.currencySymbol,
    required this.locale,
    required this.decimals,
    required this.usdRate,
    required this.tax,
  });

  factory CountryTax.fromJson(Map<String, dynamic> json) => CountryTax(
    currency: json['currency'] as String,
    currencySymbol: json['currencySymbol'] as String,
    locale: json['locale'] as String,
    decimals: json['decimals'] as int,
    usdRate: (json['usdRate'] as num).toDouble(),
    tax: TaxInfo.fromJson(json['tax'] as Map<String, dynamic>),
  );
}
