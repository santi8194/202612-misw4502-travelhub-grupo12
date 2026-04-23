import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/models/categoria_habitacion.dart';
import 'package:travel_hub/models/country_tax.dart';
import 'package:travel_hub/services/catalog_service.dart';
import 'package:travel_hub/view_models/confirm_reservation_view_model.dart';

class FakeCatalogService extends CatalogService {
  FakeCatalogService({required this.onGetCategoria});

  final Future<CategoriaHabitacion> Function(String categoryId) onGetCategoria;

  @override
  Future<CategoriaHabitacion> getCategoria(String categoryId) {
    return onGetCategoria(categoryId);
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
    tax: TaxInfo(name: 'IVA', rate: 0.19, note: 'Incluye IVA y servicio.'),
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
}
