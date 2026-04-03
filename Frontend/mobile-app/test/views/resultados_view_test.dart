import 'dart:io';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/views/resultados_view.dart';
import 'package:travel_hub/view_models/search_view_model.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/services/search_service.dart';
import 'package:travel_hub/models/hotel.dart';

class MockSearchService extends Mock implements SearchService {}
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
  late MockHttpClient mockHttpClient;
  late MockHttpClientRequest mockRequest;
  late MockHttpClientResponse mockResponse;
  late MockHttpHeaders mockHeaders;

  final transparentImage = [
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
    0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
    0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
    0x42, 0x60, 0x82,
  ];

  setUpAll(() {
    registerFallbackValue(Uri());
    mockHttpClient = MockHttpClient();
    mockRequest = MockHttpClientRequest();
    mockResponse = MockHttpClientResponse();
    mockHeaders = MockHttpHeaders();

    HttpOverrides.global = TestHttpOverrides(mockHttpClient);

    when(() => mockHttpClient.getUrl(any())).thenAnswer((_) async => mockRequest);
    when(() => mockHttpClient.openUrl(any(), any())).thenAnswer((_) async => mockRequest);
    when(() => mockRequest.headers).thenReturn(mockHeaders);
    when(() => mockRequest.close()).thenAnswer((_) async => mockResponse);
    when(() => mockResponse.statusCode).thenReturn(200);
    when(() => mockResponse.contentLength).thenReturn(transparentImage.length);
    when(() => mockResponse.compressionState).thenReturn(HttpClientResponseCompressionState.notCompressed);
    when(() => mockResponse.listen(any(),
        onError: any(named: 'onError'),
        onDone: any(named: 'onDone'),
        cancelOnError: any(named: 'cancelOnError'))).thenAnswer((invocation) {
      final onData = invocation.positionalArguments[0] as void Function(List<int>);
      final onDone = invocation.namedArguments[#onDone] as void Function()?;
      return Stream<List<int>>.fromIterable([transparentImage]).listen(onData, onDone: onDone);
    });
  });

  Widget _buildTestableWidget(SearchViewModel viewModel) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<SearchViewModel>.value(value: viewModel),
      ],
      child: MaterialApp(
        locale: const Locale('es', ''),
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('es', ''),
          Locale('en', ''),
        ],
        home: const ResultadosView(),
      ),
    );
  }

  testWidgets('ResultadosView shows empty state when no results found', (WidgetTester tester) async {
    final mockService = MockSearchService();
    final viewModel = SearchViewModel(searchService: mockService);
    
    when(() => mockService.isFromCache).thenReturn(false);
    when(() => mockService.searchHotels(
      query: any(named: 'query'),
      startDate: any(named: 'startDate'),
      endDate: any(named: 'endDate'),
      guests: any(named: 'guests'),
    )).thenAnswer((_) async => []);

    viewModel.updateDestinationQuery('Empty Place');
    await viewModel.performSearch();

    await tester.pumpWidget(_buildTestableWidget(viewModel));
    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.search_off_rounded), findsOneWidget);
    expect(find.text('No hay propiedades disponibles'), findsOneWidget);
  });

  testWidgets('ResultadosView shows list of hotels when results found', (WidgetTester tester) async {
    final mockHotels = [
      Hotel(
        imageUrl: 'https://example.com/image1.jpg',
        title: 'Hotel Test 1',
        location: 'City, Country',
        amenities: ['WiFi', 'Pool'],
      ),
    ];
    final mockService = MockSearchService();
    final viewModel = SearchViewModel(searchService: mockService);
    
    when(() => mockService.isFromCache).thenReturn(false);
    when(() => mockService.searchHotels(
      query: any(named: 'query'),
      startDate: any(named: 'startDate'),
      endDate: any(named: 'endDate'),
      guests: any(named: 'guests'),
    )).thenAnswer((_) async => mockHotels);

    viewModel.updateDestinationQuery('Some Place');
    await viewModel.performSearch();

    await tester.pumpWidget(_buildTestableWidget(viewModel));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Hotel Test 1'), findsOneWidget);
    expect(find.byType(ListView), findsOneWidget);
  });
}

