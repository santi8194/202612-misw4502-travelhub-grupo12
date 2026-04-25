import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/models/categoria_habitacion.dart';
import 'package:travel_hub/models/country_tax.dart';
import 'package:travel_hub/services/catalog_service.dart';
import 'package:travel_hub/view_models/confirm_reservation_view_model.dart';

class FakeCatalogService extends CatalogService {
  FakeCatalogService({
    required this.onGetCategoria,
    this.onGetPropertyIdByCategory,
    this.onGetCategoryPricing,
  });

  final Future<CategoriaHabitacion> Function(String categoryId) onGetCategoria;
  final Future<String?> Function(String categoryId)? onGetPropertyIdByCategory;
  final Future<CategoriaPricing> Function(String propertyId, String categoryId)?
  onGetCategoryPricing;

  @override
  Future<CategoriaHabitacion> getCategoria(String categoryId) {
    return onGetCategoria(categoryId);
  }

  @override
  Future<CategoriaPricing> getCategoryPricing({
    required String propertyId,
    required String categoryId,
  }) {
    final handler = onGetCategoryPricing;
    if (handler == null) {
      return Future.error(Exception('pricing not configured in fake'));
    }
    return handler(propertyId, categoryId);
  }

  @override
  Future<String?> getPropertyIdByCategory(String categoryId) {
    final handler = onGetPropertyIdByCategory;
    if (handler == null) {
      return Future.value('prop-1');
    }
    return handler(categoryId);
  }
}

const _sampleCategory = CategoriaHabitacion(
  idCategoria: 'cat-1',
  codigoMapeoPms: 'PMS-01',
  nombreComercial: 'Suite Deluxe',
  descripcion: 'Ocean view room',
  precioBase: PrecioBase(
    monto: '100.00',
    moneda: 'USD',
    cargoServicio: '15.00',
  ),
  fotoPortadaUrl: 'https://example.com/room.jpg',
  capacidadPax: 2,
  politicaCancelacion: PoliticaCancelacion(
    diasAnticipacion: 3,
    porcentajePenalidad: '20.00',
  ),
);

const _samplePricing = CategoriaPricing(
  idCategoria: 'cat-1',
  nombreComercial: 'Suite Deluxe',
  tarifaBase: PrecioBase(
    monto: '100.00',
    moneda: 'USD',
    cargoServicio: '15.00',
  ),
  tarifaFinDeSemana: PrecioBase(
    monto: '130.00',
    moneda: 'USD',
    cargoServicio: '18.00',
  ),
  tarifaTemporadaAlta: PrecioBase(
    monto: '160.00',
    moneda: 'USD',
    cargoServicio: '22.00',
  ),
);

const _samplePricingWithoutSpecials = CategoriaPricing(
  idCategoria: 'cat-1',
  nombreComercial: 'Suite Deluxe',
  tarifaBase: PrecioBase(monto: '0.00', moneda: '', cargoServicio: '0.00'),
  tarifaFinDeSemana: PrecioBase(
    monto: '0.00',
    moneda: '',
    cargoServicio: '0.00',
  ),
  tarifaTemporadaAlta: PrecioBase(
    monto: '0.00',
    moneda: '',
    cargoServicio: '0.00',
  ),
);

final _taxConfig = {
  'Colombia': const CountryTax(
    currency: 'COP',
    currencySymbol: '\$',
    locale: 'es_CO',
    decimals: 0,
    usdRate: 4200.0,
    tax: TaxInfo(
      name: 'IVA',
      rate: 0.19,
      note: {
        'es': 'Incluye IVA y servicio.',
        'en': 'Includes VAT and service.',
      },
    ),
  ),
};

void main() {
  test('loads category on initialization and clears loading state', () async {
    final completer = Completer<CategoriaHabitacion>();
    final viewModel = ConfirmReservationViewModel(
      location: 'Cartagena, Colombia',
      categoryId: 'cat-1',
      selectedDateRange: DateTimeRange(
        start: DateTime(2026, 4, 22),
        end: DateTime(2026, 4, 24),
      ),
      guests: 2,
      catalogService: FakeCatalogService(
        onGetCategoria: (_) => completer.future,
      ),
    );

    expect(viewModel.isLoading, true);
    expect(viewModel.errorMessage, isNull);

    completer.complete(_sampleCategory);
    await Future<void>.delayed(Duration.zero);

    expect(viewModel.isLoading, false);
    expect(viewModel.categoria?.nombreComercial, 'Suite Deluxe');
  });

  test('stores error message when category loading fails', () async {
    final viewModel = ConfirmReservationViewModel(
      location: 'Cartagena, Colombia',
      categoryId: 'missing',
      selectedDateRange: DateTimeRange(
        start: DateTime(2026, 4, 22),
        end: DateTime(2026, 4, 24),
      ),
      guests: 2,
      catalogService: FakeCatalogService(
        onGetCategoria: (_) async => throw Exception('catalog failed'),
      ),
    );

    await Future<void>.delayed(Duration.zero);

    expect(viewModel.isLoading, false);
    expect(viewModel.categoria, isNull);
    expect(viewModel.errorMessage, contains('catalog failed'));
  });

  test('computePriceBreakdown converts and formats taxes by country', () async {
    final viewModel = ConfirmReservationViewModel(
      location: 'Cartagena, Colombia',
      categoryId: 'cat-1',
      selectedDateRange: DateTimeRange(
        start: DateTime(2026, 4, 22),
        end: DateTime(2026, 4, 24),
      ),
      guests: 2,
      catalogService: FakeCatalogService(
        onGetCategoria: (_) async => _sampleCategory,
      ),
    );

    await Future<void>.delayed(Duration.zero);

    final breakdown = viewModel.computePriceBreakdown(
      nights: 2,
      country: 'Colombia',
      taxConfig: _taxConfig,
      fallbackCurrency: 'USD',
      localeLanguageCode: 'es',
    );

    expect(breakdown, isNotNull);
    expect(breakdown!.currencyTag, 'COP');
    expect(breakdown.taxLabel, 'IVA (19%)');
    expect(breakdown.fmtPricePerNight, contains('420.000'));
    expect(breakdown.fmtTotal, contains('1.062.600'));
  });

  test('returns false for a second confirm attempt while busy', () async {
    final viewModel = ConfirmReservationViewModel(
      location: 'Cartagena, Colombia',
      categoryId: 'cat-1',
      selectedDateRange: DateTimeRange(
        start: DateTime(2026, 4, 22),
        end: DateTime(2026, 4, 24),
      ),
      guests: 2,
      catalogService: FakeCatalogService(
        onGetCategoria: (_) async => _sampleCategory,
      ),
    );

    await Future<void>.delayed(Duration.zero);

    final firstAttempt = viewModel.confirmReservation();

    expect(viewModel.isConfirming, true);
    expect(await viewModel.confirmReservation(), false);
    expect(await firstAttempt, true);
    expect(viewModel.isConfirming, false);
  });

  test('uses weekend pricing when reservation includes weekend', () async {
    final viewModel = ConfirmReservationViewModel(
      location: 'Cartagena, Colombia',
      categoryId: 'cat-1',
      selectedDateRange: DateTimeRange(
        start: DateTime(2026, 4, 24),
        end: DateTime(2026, 4, 26),
      ),
      guests: 2,
      catalogService: FakeCatalogService(
        onGetCategoria: (_) async => _sampleCategory,
        onGetCategoryPricing: (_, __) async => _samplePricing,
      ),
    );

    await Future<void>.delayed(Duration.zero);

    final breakdown = viewModel.computePriceBreakdown(
      nights: 2,
      country: null,
      taxConfig: _taxConfig,
      fallbackCurrency: 'USD',
      localeLanguageCode: 'en',
    );

    expect(breakdown, isNotNull);
    expect(breakdown!.fmtPricePerNight, '\$130.00');
  });

  test(
    'uses high-season pricing when reservation is in high-season months',
    () async {
      final viewModel = ConfirmReservationViewModel(
        location: 'Cartagena, Colombia',
        categoryId: 'cat-1',
        selectedDateRange: DateTimeRange(
          start: DateTime(2026, 12, 10),
          end: DateTime(2026, 12, 12),
        ),
        guests: 2,
        catalogService: FakeCatalogService(
          onGetCategoria: (_) async => _sampleCategory,
          onGetCategoryPricing: (_, __) async => _samplePricing,
        ),
      );

      await Future<void>.delayed(Duration.zero);

      final breakdown = viewModel.computePriceBreakdown(
        nights: 2,
        country: null,
        taxConfig: _taxConfig,
        fallbackCurrency: 'USD',
        localeLanguageCode: 'en',
      );

      expect(breakdown, isNotNull);
      expect(breakdown!.fmtPricePerNight, '\$160.00');
    },
  );

  test(
    'falls back to category base price when pricing values are undefined',
    () async {
      final viewModel = ConfirmReservationViewModel(
        location: 'Cartagena, Colombia',
        categoryId: 'cat-1',
        selectedDateRange: DateTimeRange(
          start: DateTime(2026, 4, 24),
          end: DateTime(2026, 4, 26),
        ),
        guests: 2,
        catalogService: FakeCatalogService(
          onGetCategoria: (_) async => _sampleCategory,
          onGetCategoryPricing: (_, __) async => _samplePricingWithoutSpecials,
        ),
      );

      await Future<void>.delayed(Duration.zero);

      final breakdown = viewModel.computePriceBreakdown(
        nights: 2,
        country: null,
        taxConfig: _taxConfig,
        fallbackCurrency: 'USD',
        localeLanguageCode: 'en',
      );

      expect(breakdown, isNotNull);
      expect(breakdown!.fmtPricePerNight, '\$100.00');
    },
  );
}
