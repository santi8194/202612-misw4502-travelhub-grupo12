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
    this.onCalculateRoomPrice,
  });

  final Future<CategoriaHabitacion> Function(String categoryId) onGetCategoria;
  final Future<String?> Function(String categoryId)? onGetPropertyIdByCategory;
  final Future<CategoriaPricing> Function(String propertyId, String categoryId)?
  onGetCategoryPricing;
  final Future<RoomPriceCalculation> Function(
    String categoryId,
    DateTime startDate,
    DateTime endDate,
    String userCountry,
  )?
  onCalculateRoomPrice;

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

  @override
  Future<RoomPriceCalculation> calculateRoomPrice({
    required String categoryId,
    required DateTime startDate,
    required DateTime endDate,
    required String userCountry,
  }) {
    final handler = onCalculateRoomPrice;
    if (handler == null) {
      return Future.value(
        const RoomPriceCalculation(
          pricePerNight: 420000,
          nights: 2,
          subtotal: 840000,
          taxesAndCharges: 222600,
          total: 1062600,
          currency: 'COP',
          currencySymbol: r'$',
          tariffType: 'BASE',
          taxName: 'IVA',
        ),
      );
    }
    return handler(categoryId, startDate, endDate, userCountry);
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

  test(
    'computePriceBreakdown uses no-country endpoint payload when country is null',
    () async {
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
          onCalculateRoomPrice: (_, __, ___, userCountry) async {
            if (userCountry.isEmpty) {
              return const RoomPriceCalculation(
                pricePerNight: 215,
                nights: 2,
                subtotal: 430,
                taxesAndCharges: 0,
                total: 430,
                currency: 'USD',
                currencySymbol: r'$',
                tariffType: 'BASE',
                taxName: null,
              );
            }
            return const RoomPriceCalculation(
              pricePerNight: 420000,
              nights: 2,
              subtotal: 840000,
              taxesAndCharges: 222600,
              total: 1062600,
              currency: 'COP',
              currencySymbol: r'$',
              tariffType: 'BASE',
              taxName: 'IVA',
            );
          },
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
      expect(breakdown!.currencyTag, 'USD');
      expect(breakdown.fmtTotal, contains(r'$ 430.00'));
    },
  );

  test(
    'computePriceBreakdown resolves country tax config case-insensitively',
    () async {
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
        country: 'colombia',
        taxConfig: _taxConfig,
        fallbackCurrency: 'USD',
        localeLanguageCode: 'es',
      );

      expect(breakdown, isNotNull);
      expect(breakdown!.taxLabel, 'IVA (19%)');
      expect(breakdown.taxNote, 'Incluye IVA y servicio.');
    },
  );

  test(
    'computePriceBreakdown derives taxes from total minus subtotal when endpoint sends 0',
    () async {
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
          onCalculateRoomPrice: (_, __, ___, ____) async {
            return const RoomPriceCalculation(
              pricePerNight: 150000,
              nights: 2,
              subtotal: 300000,
              taxesAndCharges: 0,
              total: 357000,
              currency: 'COP',
              currencySymbol: r'$',
              tariffType: 'BASE',
              taxName: 'IVA',
            );
          },
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
      expect(breakdown!.fmtTaxesAndCharges, contains('57.000'));
      expect(breakdown.fmtTotal, contains('357.000'));
    },
  );

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

  test(
    'stores error when room-price endpoint fails for all country candidates',
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
          onCalculateRoomPrice: (_, __, ___, ____) async =>
              throw Exception('calculate failed'),
        ),
      );

      await Future<void>.delayed(Duration.zero);

      expect(
        viewModel.errorMessage,
        contains('No fue posible calcular el precio'),
      );
    },
  );
}
