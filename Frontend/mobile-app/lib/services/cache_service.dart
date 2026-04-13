import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/habitacion.dart';
import '../models/location_suggestion.dart';

/// Local cache manager backed by SharedPreferences.
///
/// Stores search results and destination suggestions as JSON strings
/// so the app can serve cached data when offline.
class CacheService {
  static const String _searchPrefix = 'cache_search_';
  static const String _destinationsKey = 'cache_destinations';

  SharedPreferences? _prefs;

  /// Allow injecting SharedPreferences for testing.
  CacheService({SharedPreferences? prefs}) : _prefs = prefs;

  Future<SharedPreferences> get _preferences async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  // ── Search Results Cache ──────────────────────────────────────────────

  /// Generates a deterministic cache key from search parameters.
  String _searchCacheKey({
    required String ciudad,
    required String pais,
    required String fechaInicio,
    required String fechaFin,
    required int huespedes,
  }) {
    return '$_searchPrefix${ciudad}_${pais}_${fechaInicio}_${fechaFin}_$huespedes'
        .toLowerCase()
        .replaceAll(' ', '_');
  }

  /// Caches a list of hotel search results.
  Future<void> cacheSearchResults({
    required String ciudad,
    required String pais,
    required String fechaInicio,
    required String fechaFin,
    required int huespedes,
    required List<Habitacion> results,
  }) async {
    final prefs = await _preferences;
    final key = _searchCacheKey(
      ciudad: ciudad,
      pais: pais,
      fechaInicio: fechaInicio,
      fechaFin: fechaFin,
      huespedes: huespedes,
    );
    final jsonList = results.map((h) => h.toJson()).toList();
    await prefs.setString(key, json.encode(jsonList));
  }

  /// Retrieves cached search results, or null if not found.
  Future<List<Habitacion>?> getCachedSearchResults({
    required String ciudad,
    required String pais,
    required String fechaInicio,
    required String fechaFin,
    required int huespedes,
  }) async {
    final prefs = await _preferences;
    final key = _searchCacheKey(
      ciudad: ciudad,
      pais: pais,
      fechaInicio: fechaInicio,
      fechaFin: fechaFin,
      huespedes: huespedes,
    );
    final cached = prefs.getString(key);
    if (cached == null) return null;

    final List<dynamic> decoded = json.decode(cached);
    return decoded
        .map((j) => Habitacion.fromJson(j as Map<String, dynamic>))
        .toList();
  }

  // ── Destination Suggestions Cache ─────────────────────────────────────

  /// Caches the full list of destination suggestions.
  Future<void> cacheDestinationSuggestions(
    List<LocationSuggestion> suggestions,
  ) async {
    final prefs = await _preferences;
    final jsonList = suggestions.map((s) => s.toJson()).toList();
    await prefs.setString(_destinationsKey, json.encode(jsonList));
  }

  /// Retrieves cached suggestions and filters them locally by [query].
  Future<List<LocationSuggestion>> getCachedDestinationSuggestions(
    String query,
  ) async {
    final prefs = await _preferences;
    final cached = prefs.getString(_destinationsKey);
    if (cached == null) return [];

    final List<dynamic> decoded = json.decode(cached);
    final allSuggestions = decoded
        .map((j) => LocationSuggestion.fromJson(j as Map<String, dynamic>))
        .toList();

    if (query.isEmpty) return allSuggestions;

    final lowerQuery = query.toLowerCase();
    return allSuggestions.where((s) {
      return s.ciudad.toLowerCase().contains(lowerQuery) ||
          s.estadoProvincia.toLowerCase().contains(lowerQuery) ||
          s.pais.toLowerCase().contains(lowerQuery);
    }).toList();
  }

  /// Merges new suggestions into the existing cached list (deduplication by ciudad+pais).
  Future<void> mergeDestinationSuggestions(
    List<LocationSuggestion> newSuggestions,
  ) async {
    final prefs = await _preferences;
    final cached = prefs.getString(_destinationsKey);

    List<LocationSuggestion> existing = [];
    if (cached != null) {
      final List<dynamic> decoded = json.decode(cached);
      existing = decoded
          .map((j) => LocationSuggestion.fromJson(j as Map<String, dynamic>))
          .toList();
    }

    // Deduplicate by ciudad+estadoProvincia+pais key
    final seen = <String>{};
    for (final s in existing) {
      seen.add('${s.ciudad}|${s.estadoProvincia}|${s.pais}');
    }

    for (final s in newSuggestions) {
      final key = '${s.ciudad}|${s.estadoProvincia}|${s.pais}';
      if (!seen.contains(key)) {
        existing.add(s);
        seen.add(key);
      }
    }

    await cacheDestinationSuggestions(existing);
  }

  // ── Utilities ─────────────────────────────────────────────────────────

  /// Clears all cached data.
  Future<void> clearCache() async {
    final prefs = await _preferences;
    final keys = prefs.getKeys().where(
      (k) => k.startsWith(_searchPrefix) || k == _destinationsKey,
    );
    for (final key in keys) {
      await prefs.remove(key);
    }
  }
}
