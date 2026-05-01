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
  final Map<String, RoomPriceCalculation> _priceBreakdownByCountry = {};
  final Set<String> _countriesBeingFetched = {};

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

      await _preloadPriceBreakdown();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> confirmReservation() async {
    if (_isConfirming) return null;

    _isConfirming = true;
    notifyListeners();

    await Future.delayed(const Duration(milliseconds: 900));

    _isConfirming = false;
    notifyListeners();

    // Return a dummy reservation ID for now
    return 'RES-123456';
  }

  String _countryCacheKey(String? country) {
    final normalized = (country ?? '').trim().toLowerCase();
    return normalized.isEmpty ? '__no_country__' : normalized;
  }

  CountryTax? _resolveCountryTax(
    String? country,
    Map<String, CountryTax> taxConfig,
  ) {
    if (country == null) return null;
    final exact = taxConfig[country];
    if (exact != null) return exact;

    final key = country.trim().toLowerCase();
    for (final entry in taxConfig.entries) {
      if (entry.key.trim().toLowerCase() == key) {
        return entry.value;
      }
    }
    return null;
  }

  String _countryFromLocation() {
    final trimmed = location.trim();
    if (trimmed.isEmpty) return '';
    final split = trimmed.split(',');
    return split.isEmpty ? '' : split.last.trim();
  }

  Future<void> _preloadPriceBreakdown() async {
    final cat = _categoria;
    if (cat == null) return;

    final countryCandidates = <String>{_countryFromLocation(), ''};
    Object? lastError;

    for (final country in countryCandidates) {
      try {
        final result = await _catalogService.calculateRoomPrice(
          categoryId: cat.idCategoria,
          startDate: selectedDateRange.start,
          endDate: selectedDateRange.end,
          userCountry: country,
        );
        _priceBreakdownByCountry[_countryCacheKey(country)] = result;
      } catch (e) {
        lastError = e;
      }
    }

    if (_priceBreakdownByCountry.isEmpty && lastError != null) {
      throw Exception(
        'No fue posible calcular el precio de la reserva: $lastError',
      );
    }
  }

  Future<void> _fetchPriceBreakdownForCountry(String? country) async {
    final cat = _categoria;
    if (cat == null) return;

    final cacheKey = _countryCacheKey(country);
    if (_priceBreakdownByCountry.containsKey(cacheKey)) return;
    if (_countriesBeingFetched.contains(cacheKey)) return;

    _countriesBeingFetched.add(cacheKey);
    try {
      final result = await _catalogService.calculateRoomPrice(
        categoryId: cat.idCategoria,
        startDate: selectedDateRange.start,
        endDate: selectedDateRange.end,
        userCountry: country?.trim() ?? '',
      );
      _priceBreakdownByCountry[cacheKey] = result;
      notifyListeners();
    } catch (_) {
      // Keep the last successfully cached value without surfacing a noisy UI error.
    } finally {
      _countriesBeingFetched.remove(cacheKey);
    }
  }

  // ── Price & currency ───────────────────────────────────────────────────

  String _formatWithSymbol(
    double amount,
    String currency,
    String symbol,
    CountryTax? countryTax,
  ) {
    if (countryTax != null) {
      if (countryTax.decimals == 0) {
        return '$symbol ${NumberFormat('#,###', countryTax.locale).format(amount.round())}';
      }
      return '$symbol ${NumberFormat('#,##0.00', countryTax.locale).format(amount)}';
    }
    if (currency == 'COP') {
      return '$symbol ${NumberFormat('#,###', 'es_CO').format(amount.round())}';
    }
    return '$symbol ${NumberFormat('#,##0.00', 'en_US').format(amount)}';
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
    final countryTax = _resolveCountryTax(country, taxConfig);
    final countryKey = _countryCacheKey(country);
    if (!_priceBreakdownByCountry.containsKey(countryKey)) {
      _fetchPriceBreakdownForCountry(country);
    }

    final apiBreakdown =
        _priceBreakdownByCountry[countryKey] ??
        _priceBreakdownByCountry[_countryCacheKey(_countryFromLocation())] ??
        _priceBreakdownByCountry[_countryCacheKey(null)];
    if (apiBreakdown == null) return null;

    final preferredCurrency = countryTax?.currency ?? fallbackCurrency;
    final displayCurrency = preferredCurrency.isNotEmpty
        ? preferredCurrency
        : (apiBreakdown.currency.isNotEmpty
              ? apiBreakdown.currency
              : fallbackCurrency);
    final currencySymbol =
        countryTax?.currencySymbol ??
        (apiBreakdown.currencySymbol.isNotEmpty
            ? apiBreakdown.currencySymbol
            : r'$');

    final taxLabel = countryTax != null
        ? '${countryTax.tax.name} (${(countryTax.tax.rate * 100).toStringAsFixed(0)}%)'
        : ((apiBreakdown.taxName != null &&
                  apiBreakdown.taxName!.trim().isNotEmpty)
              ? apiBreakdown.taxName!.trim()
              : null);

    final computedTaxesAndCharges = apiBreakdown.taxesAndCharges > 0
        ? apiBreakdown.taxesAndCharges
        : ((apiBreakdown.total - apiBreakdown.subtotal) > 0
              ? (apiBreakdown.total - apiBreakdown.subtotal)
              : 0.0);

    return PriceBreakdown(
      currencyTag: displayCurrency,
      fmtPricePerNight: _formatWithSymbol(
        apiBreakdown.pricePerNight,
        displayCurrency,
        currencySymbol,
        countryTax,
      ),
      fmtSubtotal: _formatWithSymbol(
        apiBreakdown.subtotal,
        displayCurrency,
        currencySymbol,
        countryTax,
      ),
      fmtTaxesAndCharges: _formatWithSymbol(
        computedTaxesAndCharges,
        displayCurrency,
        currencySymbol,
        countryTax,
      ),
      taxLabel: taxLabel,
      fmtTotal: _formatWithSymbol(
        apiBreakdown.total,
        displayCurrency,
        currencySymbol,
        countryTax,
      ),
      taxNote: countryTax?.tax.noteForLanguage(localeLanguageCode),
    );
  }
}
