import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/categoria_habitacion.dart';
import '../models/country_tax.dart';
import '../services/catalog_service.dart';

// ── Value object returned by computePriceBreakdown ────────────────────────────

class PriceBreakdown {
  final String currencyTag;
  final String fmtPricePerNight;
  final String fmtSubtotal;
  final String fmtTaxesAndCharges;
  final String? taxLabel;
  final String fmtTotal;
  final String? taxNote;

  const PriceBreakdown({
    required this.currencyTag,
    required this.fmtPricePerNight,
    required this.fmtSubtotal,
    required this.fmtTaxesAndCharges,
    this.taxLabel,
    required this.fmtTotal,
    this.taxNote,
  });
}

class ConfirmReservationViewModel extends ChangeNotifier {
  final String location;
  final String categoryId;
  final DateTimeRange selectedDateRange;
  final int guests;
  final CatalogService _catalogService;

  bool _isLoading = false;
  bool _isConfirming = false;
  String? _errorMessage;
  CategoriaHabitacion? _categoria;
  CategoriaPricing? _categoriaPricing;

  ConfirmReservationViewModel({
    required this.location,
    required this.categoryId,
    required this.selectedDateRange,
    required this.guests,
    CatalogService? catalogService,
  }) : _catalogService = catalogService ?? CatalogService() {
    _loadCategoria();
  }

  bool get isLoading => _isLoading;
  bool get isConfirming => _isConfirming;
  String? get errorMessage => _errorMessage;
  CategoriaHabitacion? get categoria => _categoria;

  Future<void> _loadCategoria() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _categoria = await _catalogService.getCategoria(categoryId);

      final resolvedPropertyId = await _catalogService.getPropertyIdByCategory(
        _categoria!.idCategoria,
      );

      if (resolvedPropertyId != null && resolvedPropertyId.isNotEmpty) {
        try {
          _categoriaPricing = await _catalogService.getCategoryPricing(
            propertyId: resolvedPropertyId,
            categoryId: categoryId,
          );
        } catch (_) {
          // Si pricing no responde o no existe configuración, se usa precio base.
          _categoriaPricing = null;
        }
      }
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> confirmReservation() async {
    if (_isConfirming) return false;

    _isConfirming = true;
    notifyListeners();

    await Future.delayed(const Duration(milliseconds: 900));

    _isConfirming = false;
    notifyListeners();

    return true;
  }

  // ── Price & currency ───────────────────────────────────────────────────

  /// Fixed fallback rate COP↔USD when no [CountryTax] config is available.
  static const double _usdToCopFallback = 4200.0;

  static const Set<int> _highSeasonMonths = {1, 6, 7, 12};

  bool _isWeekend(DateTime day) =>
      day.weekday == DateTime.friday ||
      day.weekday == DateTime.saturday ||
      day.weekday == DateTime.sunday;

  bool _isHighSeason(DateTime day) => _highSeasonMonths.contains(day.month);

  bool _rangeMatches(bool Function(DateTime day) predicate) {
    for (
      var day = DateTime(
        selectedDateRange.start.year,
        selectedDateRange.start.month,
        selectedDateRange.start.day,
      );
      day.isBefore(selectedDateRange.end);
      day = day.add(const Duration(days: 1))
    ) {
      if (predicate(day)) return true;
    }
    return false;
  }

  bool _hasDefinedPrice(PrecioBase price) {
    final amount = double.tryParse(price.monto);
    return (amount != null && amount > 0) && price.moneda.isNotEmpty;
  }

  PrecioBase _resolveNightlyPrice(CategoriaHabitacion category) {
    final pricing = _categoriaPricing;
    if (pricing == null) return category.precioBase;

    if (_rangeMatches(_isHighSeason) &&
        _hasDefinedPrice(pricing.tarifaTemporadaAlta)) {
      return pricing.tarifaTemporadaAlta;
    }

    if (_rangeMatches(_isWeekend) &&
        _hasDefinedPrice(pricing.tarifaFinDeSemana)) {
      return pricing.tarifaFinDeSemana;
    }

    if (_hasDefinedPrice(pricing.tarifaBase)) {
      return pricing.tarifaBase;
    }

    return category.precioBase;
  }

  double _getUsdRate(String currency, Map<String, CountryTax> taxConfig) {
    if (currency == 'USD') return 1.0;
    if (currency == 'COP') return _usdToCopFallback;
    for (final c in taxConfig.values) {
      if (c.currency == currency) return c.usdRate;
    }
    return 1.0;
  }

  /// Converts [amount] from [from] to [to] using USD as pivot.
  double convertPrice(
    double amount,
    String from,
    String to,
    Map<String, CountryTax> taxConfig,
  ) {
    if (from == to) return amount;
    final fromRate = _getUsdRate(from, taxConfig);
    final toRate = _getUsdRate(to, taxConfig);
    return (amount / fromRate) * toRate;
  }

  /// Formats [amount] using [countryTax] rules, or falls back to COP/USD.
  String formatPrice(double amount, String currency, [CountryTax? countryTax]) {
    if (countryTax != null) {
      final sym = countryTax.currencySymbol;
      if (countryTax.decimals == 0) {
        return '$sym ${NumberFormat('#,###', countryTax.locale).format(amount.round())}';
      }
      return '$sym ${NumberFormat('#,##0.00', countryTax.locale).format(amount)}';
    }
    if (currency == 'COP') {
      return NumberFormat('#,###', 'es_CO').format(amount.round());
    }
    return '\$${NumberFormat('#,##0.00', 'en_US').format(amount)}';
  }

  /// Computes the full [PriceBreakdown] for the current reservation.
  ///
  /// [country] is the user-selected country (may be null).
  /// [taxConfig] is the map loaded from country_taxes.json.
  /// [fallbackCurrency] is the locale-derived fallback currency code.
  PriceBreakdown? computePriceBreakdown({
    required int nights,
    required String? country,
    required Map<String, CountryTax> taxConfig,
    required String fallbackCurrency,
    required String localeLanguageCode,
  }) {
    final cat = _categoria;
    if (cat == null) return null;

    final effectivePrice = _resolveNightlyPrice(cat);

    final countryTax = country != null ? taxConfig[country] : null;
    final sourceCurrency = effectivePrice.moneda;
    final displayCurrency = countryTax?.currency ?? fallbackCurrency;

    final pricePerNight = double.tryParse(effectivePrice.monto) ?? 0.0;
    final serviceCharge = double.tryParse(effectivePrice.cargoServicio) ?? 0.0;

    final dispPricePerNight = convertPrice(
      pricePerNight,
      sourceCurrency,
      displayCurrency,
      taxConfig,
    );
    final dispServiceCharge = convertPrice(
      serviceCharge,
      sourceCurrency,
      displayCurrency,
      taxConfig,
    );
    final dispSubtotal = nights * dispPricePerNight;
    final taxesAndCharges =
        dispSubtotal * (countryTax?.tax.rate ?? 0.0) + dispServiceCharge;
    final dispTotal = dispSubtotal + taxesAndCharges;

    final taxLabel = countryTax != null
        ? '${countryTax.tax.name} (${(countryTax.tax.rate * 100).toStringAsFixed(0)}%)'
        : null;

    return PriceBreakdown(
      currencyTag: displayCurrency,
      fmtPricePerNight: formatPrice(
        dispPricePerNight,
        displayCurrency,
        countryTax,
      ),
      fmtSubtotal: formatPrice(dispSubtotal, displayCurrency, countryTax),
      fmtTaxesAndCharges: formatPrice(
        taxesAndCharges,
        displayCurrency,
        countryTax,
      ),
      taxLabel: taxLabel,
      fmtTotal: formatPrice(dispTotal, displayCurrency, countryTax),
      taxNote: countryTax?.tax.noteForLanguage(localeLanguageCode),
    );
  }
}
