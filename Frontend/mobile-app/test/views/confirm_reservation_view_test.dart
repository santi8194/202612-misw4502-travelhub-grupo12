import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/models/categoria_habitacion.dart';
import 'package:travel_hub/models/country_tax.dart';
import 'package:travel_hub/services/catalog_service.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';
import 'package:travel_hub/views/confirm_reservation_view.dart';

class FakeCatalogService extends CatalogService {
  FakeCatalogService(this.loader);

  final Future<CategoriaHabitacion> Function(String categoryId) loader;

  @override
  Future<CategoriaHabitacion> getCategoria(String categoryId) {
    return loader(categoryId);
  }

  @override
  Future<String?> getPropertyIdByCategory(String categoryId) {
    return Future.value('prop-1');
  }

  @override
  Future<RoomPriceCalculation> calculateRoomPrice({
    required String categoryId,
    required DateTime startDate,
    required DateTime endDate,
    required String userCountry,
  }) {
    if (userCountry.isEmpty) {
      return Future.value(
        const RoomPriceCalculation(
          pricePerNight: 215,
          nights: 2,
          subtotal: 430,
          taxesAndCharges: 0,
          total: 430,
          currency: 'USD',
          currencySymbol: r'$',
          tariffType: 'BASE',
          taxName: null,
        ),
      );
    }

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
}

void main() {
  const sampleCategory = CategoriaHabitacion(
    idCategoria: 'cat-200',
    codigoMapeoPms: 'PMS-200',
    nombreComercial: 'Suite Deluxe',
    descripcion: 'Ocean view suite',
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

  final taxConfig = {
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

  Widget buildTestableWidget({
    String? country = 'Colombia',
    Locale locale = const Locale('en'),
    DateTimeRange? dateRange,
    String categoryId = 'cat-404',
    CatalogService? catalogService,
  }) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => UserPreferencesViewModel()..setCountry(country),
        ),
        Provider<Map<String, CountryTax>>.value(value: taxConfig),
      ],
      child: MaterialApp(
        locale: locale,
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('es')],
        home: ConfirmReservationView(
          location: 'Cartagena, Colombia',
          categoryId: categoryId,
          dateRange:
              dateRange ??
              DateTimeRange(
                start: DateTime(2026, 4, 22),
                end: DateTime(2026, 4, 24),
              ),
          guests: 2,
          catalogService: catalogService,
        ),
      ),
    );
  }

  testWidgets(
    'shows loading first and then an error message on catalog failure',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        buildTestableWidget(
          catalogService: FakeCatalogService(
            (_) async => throw Exception('catalog failed'),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      await tester.pumpAndSettle();

      expect(find.text('Confirm Reservation'), findsNothing);
      expect(find.byIcon(Icons.arrow_back), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
      expect(find.textContaining('catalog failed'), findsOneWidget);
    },
  );

  testWidgets('renders reservation details, pricing, and confirmation flow', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      buildTestableWidget(
        categoryId: 'cat-200',
        catalogService: FakeCatalogService((_) async => sampleCategory),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Confirm Reservation'), findsWidgets);
    expect(find.text('Suite Deluxe'), findsOneWidget);
    expect(find.text('Cartagena, Colombia'), findsOneWidget);
    expect(find.text('TRIP DETAILS'), findsOneWidget);
    expect(find.text('PRICE BREAKDOWN'), findsOneWidget);
    expect(find.text('Payment Method'), findsOneWidget);
    expect(find.text('Visa ending in •••• 4242'), findsOneWidget);
    expect(find.text('22 - 24 APR'), findsOneWidget);
    expect(find.text('2 guests'), findsOneWidget);
    expect(find.text('COP'), findsOneWidget);
    expect(find.textContaining('420.000'), findsOneWidget);
    expect(find.textContaining('1.062.600'), findsOneWidget);
    expect(find.text('Includes VAT and service.'), findsOneWidget);

    await tester.tap(
      find.widgetWithText(ElevatedButton, 'Confirm Reservation'),
    );
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 950));
    await tester.pumpAndSettle();

    expect(
      find.text('Your reservation has been confirmed successfully.'),
      findsOneWidget,
    );
  });

  testWidgets(
    'uses locale fallback currency and cross-month date format when country is not set',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        buildTestableWidget(
          categoryId: 'cat-200',
          country: null,
          catalogService: FakeCatalogService((_) async => sampleCategory),
          dateRange: DateTimeRange(
            start: DateTime(2026, 4, 30),
            end: DateTime(2026, 5, 2),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('30 APR - 2 MAY'), findsOneWidget);
      expect(find.text('USD'), findsOneWidget);
      expect(find.textContaining(r'$ 430.00'), findsWidgets);
      expect(find.text('Taxes and charges'), findsOneWidget);
    },
  );
}
