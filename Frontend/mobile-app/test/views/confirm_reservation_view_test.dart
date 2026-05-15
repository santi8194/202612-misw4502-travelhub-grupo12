import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:network_image_mock/network_image_mock.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/models/categoria_habitacion.dart';
import 'package:travel_hub/models/country_tax.dart';
import 'package:travel_hub/services/catalog_service.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';
import 'package:travel_hub/views/confirm_reservation_view.dart';

class MockCatalogService extends Mock implements CatalogService {}

class MockUserPreferencesViewModel extends Mock
    implements UserPreferencesViewModel {}

void main() {
  late MockCatalogService mockCatalog;
  late MockUserPreferencesViewModel mockUserVM;

  setUp(() {
    mockCatalog = MockCatalogService();
    mockUserVM = MockUserPreferencesViewModel();

    when(() => mockUserVM.country).thenReturn('Colombia');

    final category = CategoriaHabitacion(
      idCategoria: 'cat-1',
      codigoMapeoPms: 'map-1',
      nombreComercial: 'Test Category',
      descripcion: 'Description',
      precioBase: const PrecioBase(
        monto: '100.0',
        moneda: 'USD',
        cargoServicio: '0',
      ),
      fotoPortadaUrl: 'http://img.com',
      capacidadPax: 2,
      politicaCancelacion: const PoliticaCancelacion(
        diasAnticipacion: 1,
        porcentajePenalidad: '0',
      ),
    );

    when(
      () => mockCatalog.getCategoria('cat-1'),
    ).thenAnswer((_) async => category);
    when(
      () => mockCatalog.calculateRoomPrice(
        categoryId: 'cat-1',
        startDate: any(named: 'startDate'),
        endDate: any(named: 'endDate'),
        userCountry: any(named: 'userCountry'),
      ),
    ).thenAnswer(
      (_) async => const RoomPriceCalculation(
        pricePerNight: 50.0,
        nights: 2,
        subtotal: 100.0,
        taxesAndCharges: 19.0,
        total: 119.0,
        currency: 'USD',
        currencySymbol: r'$',
      ),
    );
  });

  Widget createWidgetUnderTest() {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<UserPreferencesViewModel>.value(
          value: mockUserVM,
        ),
        Provider<Map<String, CountryTax>>.value(value: {}),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('es')],
        locale: const Locale('es'),
        home: ConfirmReservationView(
          location: 'Test Location',
          categoryId: 'cat-1',
          dateRange: DateTimeRange(
            start: DateTime.now(),
            end: DateTime.now().add(const Duration(days: 2)),
          ),
          guests: 2,
          catalogService: mockCatalog,
        ),
      ),
    );
  }

  testWidgets('ConfirmReservationView renders correctly', (tester) async {
    await mockNetworkImagesFor(() async {
      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump(); // Start loading
      await tester.pump(); // Finish loading

      expect(find.text('Test Category'), findsOneWidget);
      expect(find.text('Test Location'), findsOneWidget);
      expect(
        find.textContaining(RegExp(r'Confirmar', caseSensitive: false)),
        findsWidgets,
      );

      // Tap confirm to test logic
      await tester.tap(
        find.textContaining(RegExp(r'Confirmar', caseSensitive: false)).first,
      );
      await tester.pump();
    });
  });
}
