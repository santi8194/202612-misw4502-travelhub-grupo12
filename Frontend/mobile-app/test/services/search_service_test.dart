import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/location_suggestion.dart';
import 'package:travel_hub/services/cache_service.dart';
import 'package:travel_hub/services/search_service.dart';

class MockHttpClient extends Mock implements http.Client {}

class MockCacheService extends Mock implements CacheService {}

void main() {
  late SearchService searchService;
  late MockHttpClient mockHttpClient;
  late MockCacheService mockCacheService;

  setUpAll(() {
    registerFallbackValue(Uri());
  });

  setUp(() {
    mockHttpClient = MockHttpClient();
    mockCacheService = MockCacheService();
    searchService = SearchService(
      httpClient: mockHttpClient,
      cacheService: mockCacheService,
    );
  });

  group('SearchService - searchHotels', () {
    final mockHotelsJson = {
      'resultados': [
        {
          'imagen_principal_url': 'http://example.com/img.jpg',
          'propiedad_nombre': 'Test Hotel',
          'ciudad': 'Medellín',
          'pais': 'Colombia',
          'amenidades_destacadas': ['WiFi', 'Pool'],
        },
      ],
    };

    test(
      'returns list of hotels and caches results on success (200)',
      () async {
        when(() => mockHttpClient.get(any())).thenAnswer(
          (_) async => http.Response(json.encode(mockHotelsJson), 200),
        );
        when(
          () => mockCacheService.cacheSearchResults(
            ciudad: any(named: 'ciudad'),
            pais: any(named: 'pais'),
            fechaInicio: any(named: 'fechaInicio'),
            fechaFin: any(named: 'fechaFin'),
            huespedes: any(named: 'huespedes'),
            results: any(named: 'results'),
          ),
        ).thenAnswer((_) async => {});

        final results = await searchService.searchHotels(
          query: 'Medellín, Colombia',
          startDate: DateTime(2024, 1, 1),
          endDate: DateTime(2024, 1, 7),
          guests: 2,
        );

        expect(results.length, 1);
        expect(results.first.title, 'Test Hotel');
        expect(searchService.isFromCache, false);

        verify(
          () => mockCacheService.cacheSearchResults(
            ciudad: 'Medellín',
            pais: 'Colombia',
            fechaInicio: '2024-01-01',
            fechaFin: '2024-01-07',
            huespedes: 2,
            results: any(named: 'results'),
          ),
        ).called(1);
      },
    );

    test('falls back to cache on SocketException (Network Error)', () async {
      final cachedHotels = [
        Habitacion(
          imageUrl: 'cache_url',
          title: 'Cached Hotel',
          location: 'Medellín, Colombia',
          amenities: ['WiFi'],
          price: 120.0,
        ),
      ];

      when(
        () => mockHttpClient.get(any()),
      ).thenThrow(const SocketException('No Internet'));
      when(
        () => mockCacheService.getCachedSearchResults(
          ciudad: any(named: 'ciudad'),
          pais: any(named: 'pais'),
          fechaInicio: any(named: 'fechaInicio'),
          fechaFin: any(named: 'fechaFin'),
          huespedes: any(named: 'huespedes'),
        ),
      ).thenAnswer((_) async => cachedHotels);

      final results = await searchService.searchHotels(
        query: 'Medellín, Colombia',
        startDate: DateTime(2024, 1, 1),
        endDate: DateTime(2024, 1, 7),
        guests: 2,
      );

      expect(results.length, 1);
      expect(results.first.title, 'Cached Hotel');
      expect(searchService.isFromCache, true);
    });

    test('throws Exception on HTTP error status (e.g. 500)', () async {
      when(
        () => mockHttpClient.get(any()),
      ).thenAnswer((_) async => http.Response('Internal Server Error', 500));
      // It should also try to fall back to cache on error status according to implementation
      when(
        () => mockCacheService.getCachedSearchResults(
          ciudad: any(named: 'ciudad'),
          pais: any(named: 'pais'),
          fechaInicio: any(named: 'fechaInicio'),
          fechaFin: any(named: 'fechaFin'),
          huespedes: any(named: 'huespedes'),
        ),
      ).thenAnswer((_) async => null);

      expect(
        () => searchService.searchHotels(
          query: 'Medellín, Colombia',
          startDate: DateTime(2024, 1, 1),
          endDate: DateTime(2024, 1, 7),
          guests: 2,
        ),
        throwsException,
      );
    });
  });

  group('SearchService - getLocationSuggestions', () {
    final mockSuggestionsJson = {
      'results': [
        {
          'ciudad': 'Medellín',
          'estado_provincia': 'Antioquia',
          'pais': 'Colombia',
        },
      ],
    };

    test(
      'returns logic suggestions and merges them into cache on success',
      () async {
        when(
          () => mockHttpClient.get(any(), headers: any(named: 'headers')),
        ).thenAnswer(
          (_) async => http.Response(json.encode(mockSuggestionsJson), 200),
        );
        when(
          () => mockCacheService.mergeDestinationSuggestions(any()),
        ).thenAnswer((_) async => {});
        when(
          () => mockCacheService.getCachedDestinationSuggestions(any()),
        ).thenAnswer((_) async => []);

        final suggestions = await searchService.getLocationSuggestions('Med');

        expect(suggestions.length, 1);
        expect(suggestions.first.ciudad, 'Medellín');
        verify(
          () => mockCacheService.mergeDestinationSuggestions(any()),
        ).called(1);
      },
    );

    test('falls back to cached suggestions on network failure', () async {
      final cachedSuggestions = [
        const LocationSuggestion(
          ciudad: 'MockCity',
          estadoProvincia: 'MockState',
          pais: 'MockCountry',
        ),
      ];

      when(
        () => mockHttpClient.get(any(), headers: any(named: 'headers')),
      ).thenThrow(const SocketException('Offline'));
      when(
        () => mockCacheService.getCachedDestinationSuggestions(any()),
      ).thenAnswer((_) async => cachedSuggestions);

      final suggestions = await searchService.getLocationSuggestions('Mock');

      expect(suggestions.length, 1);
      expect(suggestions.first.ciudad, 'MockCity');
      expect(searchService.isFromCache, true);
    });
  });
}
