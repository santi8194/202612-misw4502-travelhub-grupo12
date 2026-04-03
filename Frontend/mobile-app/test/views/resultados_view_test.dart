import 'dart:io';
import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/views/resultados_view.dart';
import 'package:travel_hub/view_models/search_view_model.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/services/search_service.dart';
import 'package:travel_hub/models/hotel.dart';

class MockSearchService extends SearchService {
  final List<Hotel> mockResults;
  
  MockSearchService({this.mockResults = const []});

  @override
  Future<List<Hotel>> searchHotels({
    required query,
    required startDate,
    required endDate,
    required guests,
  }) async => mockResults;
}

// Simple Mock that uses noSuchMethod to avoid implementing the whole HttpClient interface
class MockHttpClient implements HttpClient {
  @override
  Future<HttpClientRequest> getUrl(Uri url) => Future.value(MockHttpClientRequest());
  
  @override
  Future<HttpClientRequest> openUrl(String method, Uri url) => Future.value(MockHttpClientRequest());
  
  @override
  dynamic noSuchMethod(Invocation invocation) {
    if (invocation.memberName == #getUrl || invocation.memberName == #openUrl || invocation.memberName == #get) {
      return Future.value(MockHttpClientRequest());
    }
    return super.noSuchMethod(invocation);
  }
}

class MockHttpClientRequest implements HttpClientRequest {
  @override
  HttpHeaders get headers => MockHttpHeaders();

  @override
  Future<HttpClientResponse> close() => Future.value(MockHttpClientResponse());

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockHttpClientResponse extends Stream<List<int>> implements HttpClientResponse {
  @override
  int get statusCode => 200;

  @override
  int get contentLength => _transparentImage.length;

  @override
  HttpHeaders get headers => MockHttpHeaders();

  static final List<int> _transparentImage = [
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
    0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
    0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
    0x42, 0x60, 0x82,
  ];

  @override
  StreamSubscription<List<int>> listen(void Function(List<int> event)? onData,
      {Function? onError, void Function()? onDone, bool? cancelOnError}) {
    return Stream.fromIterable([_transparentImage]).listen(onData,
        onError: onError, onDone: onDone, cancelOnError: cancelOnError);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockHttpHeaders implements HttpHeaders {
  @override
  List<String>? operator [](String name) => null;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class TestHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) => MockHttpClient();
}

void main() {
  setUpAll(() {
    HttpOverrides.global = TestHttpOverrides();
  });

  testWidgets('ResultadosView shows empty state when no results found', (WidgetTester tester) async {
    final viewModel = SearchViewModel(searchService: MockSearchService(mockResults: []));
    
    viewModel.updateDestinationQuery('Empty Place');
    await viewModel.performSearch();

    await tester.pumpWidget(
      MultiProvider(
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
      ),
    );

    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.search_off_rounded), findsOneWidget);
    expect(find.text('No hay propiedades disponibles'), findsOneWidget);
    expect(find.textContaining('No se encontraron propiedades'), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);
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
    final viewModel = SearchViewModel(searchService: MockSearchService(mockResults: mockHotels));
    
    viewModel.updateDestinationQuery('Some Place');
    await viewModel.performSearch();

    await tester.pumpWidget(
      MultiProvider(
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
      ),
    );

    await tester.pump();

    expect(find.text('Hotel Test 1'), findsOneWidget);
    expect(find.byType(ListView), findsOneWidget);
  });
}



