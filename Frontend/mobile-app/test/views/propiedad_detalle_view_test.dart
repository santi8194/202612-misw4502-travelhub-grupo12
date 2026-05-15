import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:network_image_mock/network_image_mock.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/models/country_tax.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/services/catalog_service.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';
import 'package:travel_hub/views/propiedad_detalle_view.dart';

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

    final detail = {
      'propiedad': {
        'nombre': 'Test Hotel',
        'estrellas': 4,
        'ubicacion': {'ciudad': 'Bogotá', 'pais': 'Colombia'},
      },
      'categoria': {
        'descripcion': 'Desc',
        'precio_base': {'monto': '100', 'moneda': 'USD'},
      },
      'rating_promedio': 4.5,
      'total_resenas': 10,
      'galeria': [
        {'url_full': 'http://img.com'},
      ],
      'amenidades': [
        {'nombre': 'Wifi', 'icono': 'wifi'},
      ],
    };

    when(
      () => mockCatalog.getPropertyDetail(any()),
    ).thenAnswer((_) async => detail);
  });

  Widget createWidgetUnderTest() {
    final hotel = Habitacion(
      title: 'Test Hotel',
      location: 'Test Loc',
      imageUrl: 'http://img.com',
      price: 100,
      amenities: ['Wifi', 'Pool'],
      categoryId: 'cat-1',
    );

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
        home: PropiedadDetalleView(
          habitacion: hotel,
          guests: 2,
          catalogService: mockCatalog,
        ),
      ),
    );
  }

  testWidgets('PropiedadDetalleView renders hotel info', (tester) async {
    await mockNetworkImagesFor(() async {
      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump(); // Start loading
      await tester.pump(); // Finish loading

      expect(find.text('Test Hotel'), findsWidgets);
      expect(find.text('Sobre la propiedad'), findsOneWidget);
    });
  });

  testWidgets('PropiedadDetalleView switches tabs', (tester) async {
    await mockNetworkImagesFor(() async {
      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Habitaciones'));
      await tester.pumpAndSettle();
      expect(find.text('Galería de Habitaciones'), findsOneWidget);

      await tester.tap(find.text('Reseñas'));
      await tester.pumpAndSettle();
      expect(find.text('10 RESEÑAS VERIFICADAS'), findsOneWidget);
    });
  });

  testWidgets('PropiedadDetalleView shows error state', (tester) async {
    when(
      () => mockCatalog.getPropertyDetail(any()),
    ).thenThrow(Exception('Error from API'));

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump(); // Start loading
    await tester.pumpAndSettle(); // Finish loading

    expect(find.textContaining('Error from API'), findsOneWidget);
  });

  testWidgets('PropiedadDetalleView opens full screen image', (tester) async {
    await mockNetworkImagesFor(() async {
      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pumpAndSettle();

      final images = find.byType(Image);
      expect(images, findsWidgets);

      await tester.tap(images.first);
      await tester.pumpAndSettle();

      expect(find.byType(InteractiveViewer), findsOneWidget);

      final closeIcon = find.byIcon(Icons.close);
      await tester.tap(closeIcon);
      await tester.pumpAndSettle();

      expect(find.byType(InteractiveViewer), findsNothing);
    });
  });
}
