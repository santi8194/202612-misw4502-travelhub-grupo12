class TaxInfo {
  final String name;
  final double rate;
  final String note;

  const TaxInfo({
    required this.name,
    required this.rate,
    required this.note,
  });

  factory TaxInfo.fromJson(Map<String, dynamic> json) => TaxInfo(
        name: json['name'] as String,
        rate: (json['rate'] as num).toDouble(),
        note: json['note'] as String,
      );
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
