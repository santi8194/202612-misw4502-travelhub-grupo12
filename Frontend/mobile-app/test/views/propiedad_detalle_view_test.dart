import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/services/catalog_service.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';
import 'package:travel_hub/views/confirm_reservation_view.dart';
import 'package:travel_hub/views/propiedad_detalle_view.dart';

class MockCatalogService extends Mock implements CatalogService {}

class MockUserPreferencesViewModel extends Mock
    implements UserPreferencesViewModel {}

class MockHttpClient extends Mock implements HttpClient {}

class MockHttpClientRequest extends Mock implements HttpClientRequest {}

class MockHttpClientResponse extends Mock implements HttpClientResponse {}

class MockHttpHeaders extends Mock implements HttpHeaders {}

class TestHttpOverrides extends HttpOverrides {
  final HttpClient client;
  TestHttpOverrides(this.client);
  @override
  HttpClient createHttpClient(SecurityContext? context) => client;
}

void main() {
  late MockCatalogService mockCatalogService;
  late MockUserPreferencesViewModel mockUserPreferencesViewModel;
  late Habitacion testHabitacion;
  late MockHttpClient mockHttpClient;
  late MockHttpClientRequest mockRequest;
  late MockHttpClientResponse mockResponse;
  late MockHttpHeaders mockHeaders;

  final transparentImage = [
    0x89,
    0x50,
    0x4E,
    0x47,
    0x0D,
    0x0A,
    0x1A,
    0x0A,
    0x00,
    0x00,
    0x00,
    0x0D,
    0x49,
    0x48,
    0x44,
    0x52,
    0x00,
    0x00,
    0x00,
    0x01,
    0x00,
    0x00,
    0x00,
    0x01,
    0x08,
    0x06,
    0x00,
    0x00,
    0x00,
    0x1F,
    0x15,
    0xC4,
    0x89,
    0x00,
    0x00,
    0x00,
    0x0A,
    0x49,
    0x44,
    0x41,
    0x54,
    0x78,
    0x9C,
    0x63,
    0x00,
    0x01,
    0x00,
    0x00,
    0x05,
    0x00,
    0x01,
    0x0D,
    0x0A,
    0x2D,
    0xB4,
    0x00,
    0x00,
    0x00,
    0x00,
    0x49,
    0x45,
    0x4E,
    0x44,
    0xAE,
    0x42,
    0x60,
    0x82,
  ];

  setUpAll(() {
    registerFallbackValue(Uri());
    mockHttpClient = MockHttpClient();
    mockRequest = MockHttpClientRequest();
    mockResponse = MockHttpClientResponse();
    mockHeaders = MockHttpHeaders();

    HttpOverrides.global = TestHttpOverrides(mockHttpClient);

    when(
      () => mockHttpClient.getUrl(any()),
    ).thenAnswer((_) async => mockRequest);
    when(
      () => mockHttpClient.openUrl(any(), any()),
    ).thenAnswer((_) async => mockRequest);
    when(() => mockRequest.headers).thenReturn(mockHeaders);
    when(() => mockRequest.close()).thenAnswer((_) async => mockResponse);
    when(() => mockResponse.statusCode).thenReturn(200);
    when(() => mockResponse.contentLength).thenReturn(transparentImage.length);
    when(
      () => mockResponse.compressionState,
    ).thenReturn(HttpClientResponseCompressionState.notCompressed);
    when(
      () => mockResponse.listen(
        any(),
        onError: any(named: 'onError'),
        onDone: any(named: 'onDone'),
        cancelOnError: any(named: 'cancelOnError'),
      ),
    ).thenAnswer((invocation) {
      final onData =
          invocation.positionalArguments[0] as void Function(List<int>);
      final onDone = invocation.namedArguments[#onDone] as void Function()?;
      return Stream<List<int>>.fromIterable([
        transparentImage,
      ]).listen(onData, onDone: onDone);
    });
  });

  setUp(() {
    mockCatalogService = MockCatalogService();
    mockUserPreferencesViewModel = MockUserPreferencesViewModel();
    when(() => mockUserPreferencesViewModel.country).thenReturn('Colombia');

    testHabitacion = Habitacion(
      imageUrl: 'https://example.com/image.jpg',
      title: 'Test Hotel',
      location: 'Test City, Test Country',
      amenities: ['Wifi', 'Pool'],
      price: 100.0,
      categoryId: 'cat-123',
    );
  });

  Widget createWidgetUnderTest() {
    return ChangeNotifierProvider<UserPreferencesViewModel>.value(
      value: mockUserPreferencesViewModel,
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
          habitacion: testHabitacion,
          guests: 2,
          catalogService: mockCatalogService,
        ),
      ),
    );
  }

  final mockDetailResponse = {
    'propiedad': {
      'nombre': 'Luxury Palace',
      'estrellas': 4,
      'ubicacion': {'ciudad': 'Bogotá', 'pais': 'Colombia'},
    },
    'categoria': {
      'descripcion': 'A beautiful luxury room with all amenities.',
      'precio_base': {'monto': '150.0'},
    },
    'rating_promedio': 4.5,
    'total_resenas': 10,
    'galeria': [
      {'url_full': 'https://example.com/gallery1.jpg'},
      {'url_full': 'https://example.com/gallery2.jpg'},
      {'url_full': 'https://example.com/gallery3.jpg'},
    ],
    'amenidades': [
      {'nombre': 'Wifi', 'icono': 'wifi'},
      {'nombre': 'Piscina', 'icono': 'pool'},
    ],
    'resenas': [
      {
        'nombre_autor': 'John Doe',
        'calificacion': 5.0,
        'comentario': 'Excellent stay!',
        'fecha_creacion': '2024-04-24T10:00:00Z',
      },
    ],
  };

  testWidgets('shows loading indicator initially', (WidgetTester tester) async {
    when(() => mockCatalogService.getPropertyDetail(any())).thenAnswer(
      (_) =>
          Future.delayed(const Duration(seconds: 1), () => mockDetailResponse),
    );

    await tester.pumpWidget(createWidgetUnderTest());

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pumpAndSettle();
  });

  testWidgets('shows error message when fetching details fails', (
    WidgetTester tester,
  ) async {
    when(
      () => mockCatalogService.getPropertyDetail(any()),
    ).thenThrow(Exception('Failed to fetch details'));

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pumpAndSettle();

    expect(
      find.textContaining('Exception: Failed to fetch details'),
      findsOneWidget,
    );
  });

  testWidgets('renders property details correctly on success', (
    WidgetTester tester,
  ) async {
    when(
      () => mockCatalogService.getPropertyDetail(any()),
    ).thenAnswer((_) async => mockDetailResponse);

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pumpAndSettle();

    // Verify main info
    expect(find.text('Luxury Palace'), findsOneWidget);
    expect(find.text('Bogotá, Colombia'), findsOneWidget);
    expect(
      find.text('A beautiful luxury room with all amenities.'),
      findsOneWidget,
    );

    // Verify amenities
    expect(find.text('WIFI'), findsOneWidget);
    expect(find.text('PISCINA'), findsOneWidget);
  });

  testWidgets('switches between tabs correctly', (WidgetTester tester) async {
    when(
      () => mockCatalogService.getPropertyDetail(any()),
    ).thenAnswer((_) async => mockDetailResponse);

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pumpAndSettle();

    // Initially on Info tab (About Property text should be visible - localized in ES is "Sobre la propiedad")
    expect(find.text('Sobre la propiedad'), findsOneWidget);

    // Switch to Rooms tab
    await tester.tap(find.text('Habitaciones'));
    await tester.pumpAndSettle();
    expect(find.text('Galería de Habitaciones'), findsOneWidget);

    // Switch to Reviews tab
    await tester.tap(find.text('Reseñas'));
    await tester.pumpAndSettle();
    expect(find.textContaining('RESEÑAS VERIFICADAS'), findsOneWidget);
    expect(find.text('John Doe'), findsOneWidget);
    expect(find.text('Excellent stay!'), findsOneWidget);
  });

  testWidgets(
    'navigates to ConfirmReservationView when Reserve Now is pressed',
    (WidgetTester tester) async {
      when(
        () => mockCatalogService.getPropertyDetail(any()),
      ).thenAnswer((_) async => mockDetailResponse);

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pumpAndSettle();

      final reserveButton = find.text('Reservar Ahora');
      await tester.tap(reserveButton);
      await tester.pumpAndSettle();

      expect(find.byType(ConfirmReservationView), findsOneWidget);
    },
  );

  testWidgets('opens full screen image when gallery image is tapped', (
    WidgetTester tester,
  ) async {
    when(
      () => mockCatalogService.getPropertyDetail(any()),
    ).thenAnswer((_) async => mockDetailResponse);

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pumpAndSettle();

    // Switch to Rooms tab to find a more accessible image
    await tester.tap(find.text('Habitaciones'));
    await tester.pumpAndSettle();

    // Find the first image in the Rooms tab
    // We use find.byType(Image) and filter for one that is likely in the gallery
    final imageFinder = find.byType(Image).at(1); // skip the one in the header
    await tester.ensureVisible(imageFinder);
    await tester.pumpAndSettle();

    await tester.tap(imageFinder, warnIfMissed: false);
    await tester.pumpAndSettle();

    // Verify the full screen dialog is shown by looking for the close icon
    expect(find.byIcon(Icons.close), findsOneWidget);

    // Close the dialog
    await tester.tap(find.byIcon(Icons.close));
    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.close), findsNothing);
  });

  testWidgets('handles missing category ID gracefully', (
    WidgetTester tester,
  ) async {
    final habitacionNoId = Habitacion(
      imageUrl: 'https://example.com/image.jpg',
      title: 'No ID Hotel',
      location: 'Ghost Town',
      amenities: [],
      price: 0.0,
      categoryId: null,
    );

    await tester.pumpWidget(
      ChangeNotifierProvider<UserPreferencesViewModel>.value(
        value: mockUserPreferencesViewModel,
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
            habitacion: habitacionNoId,
            guests: 2,
            catalogService: mockCatalogService,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('No category ID available'), findsOneWidget);
  });
}
