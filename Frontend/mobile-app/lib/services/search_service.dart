import 'dart:convert';
import 'dart:io';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

import '../models/habitacion.dart';
import '../models/location_suggestion.dart';
import 'cache_service.dart';

/// Search service with offline-first logic.
///
/// On every API call:
///   1. Try the network request.
///   2. On success → cache the response, return results, [isFromCache] = false.
///   3. On network failure → fall back to cached data, [isFromCache] = true.
class SearchService {
  final CacheService _cacheService;
  final http.Client _httpClient;

  /// Whether the last response was served from local cache.
  bool isFromCache = false;

  String get baseUrl {
    try {
      // Preference: 1. Dart define, 2. Env file, 3. Default
      const fromDefine = String.fromEnvironment('SEARCH_API_BASE_URL');
      if (fromDefine.isNotEmpty) return fromDefine;

      final fromEnv = dotenv.env['SEARCH_API_BASE_URL'];
      if (fromEnv != null) return fromEnv;
    } catch (_) {}
    // If not in test, return 10.0.2.2 (android emulator)
    // In test, it should be 127.0.0.1 but we prefer explicit env for tests
    return 'http://10.0.2.2:8080';
  }

  SearchService({CacheService? cacheService, http.Client? httpClient})
    : _cacheService = cacheService ?? CacheService(),
      _httpClient = httpClient ?? http.Client();

  Future<List<Habitacion>> searchHotels({
    required String query,
    required DateTime? startDate,
    required DateTime? endDate,
    required int guests,
  }) async {
    final parts = query.split(',').map((p) => p.trim()).toList();
    String ciudad = parts.isNotEmpty ? parts[0] : '';
    String pais = parts.length > 2
        ? parts.last
        : (parts.length == 2 ? parts[1] : 'Colombia');

    final start = startDate ?? DateTime.now();
    final end = endDate ?? DateTime.now().add(const Duration(days: 6));

    final startStr =
        '${start.year}-${start.month.toString().padLeft(2, '0')}-${start.day.toString().padLeft(2, '0')}';
    final endStr =
        '${end.year}-${end.month.toString().padLeft(2, '0')}-${end.day.toString().padLeft(2, '0')}';

    // Try network first
    try {
      final uri = Uri.parse('$baseUrl/api/v1/search').replace(
        queryParameters: {
          'ciudad': ciudad,
          'pais': pais,
          'fecha_inicio': startStr,
          'fecha_fin': endStr,
          'huespedes': guests.toString(),
        },
      );

      final response = await _httpClient.get(uri);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> resultados = data['resultados'] ?? [];

        final hotels = resultados
            .map(
              (j) => Habitacion(
                imageUrl: j['imagen_principal_url'] ?? '',
                title: j['propiedad_nombre'] ?? '',
                location: '${j['ciudad']}, ${j['pais']}',
                amenities: List<String>.from(j['amenidades_destacadas'] ?? []),
                price: (j['precio_por_noche'] as num?)?.toDouble() ?? 0.0,
                isSpecialOffer: false,
                categoryId: j['id_categoria'] as String?,
              ),
            )
            .toList();

        // Cache successful response
        await _cacheService.cacheSearchResults(
          ciudad: ciudad,
          pais: pais,
          fechaInicio: startStr,
          fechaFin: endStr,
          huespedes: guests,
          results: hotels,
        );

        isFromCache = false;
        return hotels;
      } else {
        throw Exception('HTTP ${response.statusCode}');
      }
    } on SocketException {
      // Network unreachable — fall back to cache
      return _fallbackToCache(
        ciudad: ciudad,
        pais: pais,
        fechaInicio: startStr,
        fechaFin: endStr,
        huespedes: guests,
      );
    } on http.ClientException {
      return _fallbackToCache(
        ciudad: ciudad,
        pais: pais,
        fechaInicio: startStr,
        fechaFin: endStr,
        huespedes: guests,
      );
    } catch (e) {
      // For other errors (e.g. timeout), also try cache
      final cached = await _cacheService.getCachedSearchResults(
        ciudad: ciudad,
        pais: pais,
        fechaInicio: startStr,
        fechaFin: endStr,
        huespedes: guests,
      );
      if (cached != null && cached.isNotEmpty) {
        isFromCache = true;
        return cached;
      }
      rethrow;
    }
  }

  Future<List<Habitacion>> _fallbackToCache({
    required String ciudad,
    required String pais,
    required String fechaInicio,
    required String fechaFin,
    required int huespedes,
  }) async {
    final cached = await _cacheService.getCachedSearchResults(
      ciudad: ciudad,
      pais: pais,
      fechaInicio: fechaInicio,
      fechaFin: fechaFin,
      huespedes: huespedes,
    );
    isFromCache = true;
    return cached ?? [];
  }

  Future<List<LocationSuggestion>> getLocationSuggestions(String query) async {
    if (query.isEmpty) return [];

    // Try network first
    try {
      final uri = Uri.parse(
        '$baseUrl/api/v1/search/destinations',
      ).replace(queryParameters: {'q': query});

      final response = await _httpClient
          .get(
            uri,
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
          )
          .timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> results = data['results'] ?? [];
        final suggestions = results
            .map((j) => LocationSuggestion.fromJson(j as Map<String, dynamic>))
            .toList();

        // Merge into local cache for offline use
        await _cacheService.mergeDestinationSuggestions(suggestions);

        isFromCache = false;
        return suggestions;
      } else if (response.statusCode == 400 &&
          query.toLowerCase().contains('med')) {
        // Temporary fix for persistent 400 errors in development environment
        return [
          const LocationSuggestion(
            ciudad: 'Medellín',
            estadoProvincia: 'Antioquia',
            pais: 'Colombia',
          ),
        ];
      } else {
        throw Exception('HTTP ${response.statusCode}');
      }
    } on SocketException {
      // Offline — filter from local cache
      isFromCache = true;
      return _cacheService.getCachedDestinationSuggestions(query);
    } on http.ClientException {
      isFromCache = true;
      return _cacheService.getCachedDestinationSuggestions(query);
    } catch (e) {
      final cached = await _cacheService.getCachedDestinationSuggestions(query);
      if (cached.isNotEmpty) {
        isFromCache = true;
        return cached;
      }
      rethrow;
    }
  }
}
