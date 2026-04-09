import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/location_suggestion.dart';
import 'package:travel_hub/services/cache_service.dart';

class MockSharedPreferences extends Mock implements SharedPreferences {}

void main() {
  late MockSharedPreferences mockPrefs;
  late CacheService cacheService;

  setUp(() {
    mockPrefs = MockSharedPreferences();
    cacheService = CacheService(prefs: mockPrefs);
  });

  group('CacheService Tests', () {
    test('cacheSearchResults stores JSON in SharedPreferences', () async {
      final hotel = Habitacion(
        imageUrl: 'url',
        title: 'Title',
        location: 'Loc',
        amenities: [],
      );

      when(
        () => mockPrefs.setString(any(), any()),
      ).thenAnswer((_) async => true);

      await cacheService.cacheSearchResults(
        ciudad: 'Bogota',
        pais: 'Colombia',
        fechaInicio: '2024-01-01',
        fechaFin: '2024-01-05',
        huespedes: 2,
        results: [hotel],
      );

      verify(
        () => mockPrefs.setString(
          any(that: contains('bogota_colombia_2024-01-01_2024-01-05_2')),
          any(that: contains('Title')),
        ),
      ).called(1);
    });

    test('getCachedSearchResults returns list of hotels', () async {
      final jsonStr = json.encode([
        {
          'imageUrl': 'url',
          'title': 'Cached Hotel',
          'location': 'Loc',
          'amenities': [],
          'isSpecialOffer': false,
        },
      ]);

      when(() => mockPrefs.getString(any())).thenReturn(jsonStr);

      final results = await cacheService.getCachedSearchResults(
        ciudad: 'Bogota',
        pais: 'Colombia',
        fechaInicio: '2024-01-01',
        fechaFin: '2024-01-05',
        huespedes: 2,
      );

      expect(results, isNotNull);
      expect(results!.first.title, 'Cached Hotel');
    });

    test(
      'cacheDestinationSuggestions and getCachedDestinationSuggestions',
      () async {
        const suggestion = LocationSuggestion(
          ciudad: 'Medellin',
          estadoProvincia: 'Antioquia',
          pais: 'Colombia',
        );

        when(
          () => mockPrefs.setString(any(), any()),
        ).thenAnswer((_) async => true);
        when(
          () => mockPrefs.getString(any()),
        ).thenReturn(json.encode([suggestion.toJson()]));

        await cacheService.cacheDestinationSuggestions([suggestion]);
        final results = await cacheService.getCachedDestinationSuggestions(
          'Mede',
        );

        expect(results.length, 1);
        expect(results.first.ciudad, 'Medellin');
      },
    );

    test('mergeDestinationSuggestions deduplicates', () async {
      const s1 = LocationSuggestion(
        ciudad: 'C1',
        estadoProvincia: 'E1',
        pais: 'P1',
      );
      const s2 = LocationSuggestion(
        ciudad: 'C2',
        estadoProvincia: 'E2',
        pais: 'P2',
      );

      when(
        () => mockPrefs.getString(any()),
      ).thenReturn(json.encode([s1.toJson()]));
      when(
        () => mockPrefs.setString(any(), any()),
      ).thenAnswer((_) async => true);

      await cacheService.mergeDestinationSuggestions([s1, s2]);

      // Should call cacheDestinationSuggestions with both s1 and s2
      verify(
        () => mockPrefs.setString(any(), any(that: contains('C2'))),
      ).called(1);
    });

    test('clearCache removes relevant keys', () async {
      when(
        () => mockPrefs.getKeys(),
      ).thenReturn({'cache_search_test', 'other_key', 'cache_destinations'});
      when(() => mockPrefs.remove(any())).thenAnswer((_) async => true);

      await cacheService.clearCache();

      verify(() => mockPrefs.remove('cache_search_test')).called(1);
      verify(() => mockPrefs.remove('cache_destinations')).called(1);
      verifyNever(() => mockPrefs.remove('other_key'));
    });
  });
}
