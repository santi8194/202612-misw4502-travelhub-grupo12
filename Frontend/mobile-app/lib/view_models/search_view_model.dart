import 'dart:async';

import 'package:flutter/material.dart';

import '../models/habitacion.dart';
import '../models/location_suggestion.dart';
import '../services/connectivity_service.dart';
import '../services/search_service.dart';

class SearchViewModel extends ChangeNotifier {
  final SearchService _searchService;
  final ConnectivityService _connectivityService;
  StreamSubscription<bool>? _connectivitySubscription;

  // Search Form State
  String _destinationQuery = '';
  DateTimeRange? _selectedDateRange;
  int _guestCount = 2;

  // Data State
  List<Habitacion> _searchResults = [];

  // Loading States
  bool _isSearching = false;
  bool _isDestinationError = false;

  // Connectivity / Cache State
  bool _isOffline = false;
  bool _isFromCache = false;
  bool _hasPerformedSearch = false;

  // Getters
  String get destinationQuery => _destinationQuery;
  DateTimeRange? get selectedDateRange => _selectedDateRange;
  int get guestCount => _guestCount;
  List<Habitacion> get searchResults => _searchResults;
  bool get isSearching => _isSearching;
  bool get isDestinationError => _isDestinationError;
  bool get isOffline => _isOffline;
  bool get isFromCache => _isFromCache;
  bool get hasNoResults =>
      _hasPerformedSearch && _searchResults.isEmpty && !_isSearching;

  SearchViewModel({
    SearchService? searchService,
    ConnectivityService? connectivityService,
  }) : _searchService = searchService ?? SearchService(),
       _connectivityService = connectivityService ?? ConnectivityService() {
    _isOffline = !_connectivityService.isOnline;
    _listenToConnectivity();
  }

  void _listenToConnectivity() {
    _connectivitySubscription = _connectivityService.onConnectivityChanged
        .listen((isOnline) {
          final wasOffline = _isOffline;
          _isOffline = !isOnline;
          notifyListeners();

          // Auto-sync: if we just came back online and last results were cached,
          // re-execute the search to get fresh data.
          if (wasOffline && isOnline && _isFromCache && _hasPerformedSearch) {
            _syncAfterReconnection();
          }
        });
  }

  Future<void> _syncAfterReconnection() async {
    debugPrint('ConnectivitySync: Back online — refreshing cached search.');
    await performSearch();
  }

  // Setters
  void updateDestinationQuery(String query) {
    _destinationQuery = query;
    if (_destinationQuery.trim().isNotEmpty) {
      _isDestinationError = false;
    }
    notifyListeners();
  }

  void updateDateRange(DateTimeRange? range) {
    _selectedDateRange = range;
    notifyListeners();
  }

  void updateGuestCount(int count) {
    _guestCount = count;
    notifyListeners();
  }

  // API Actions
  Future<List<LocationSuggestion>> fetchLocationSuggestions(
    String query,
  ) async {
    if (query.length < 3) return [];
    try {
      final suggestions = await _searchService.getLocationSuggestions(query);
      _isFromCache = _searchService.isFromCache;
      return suggestions;
    } catch (e) {
      debugPrint('Error loading suggestions: $e');
      return [];
    }
  }

  Future<bool> performSearch() async {
    if (_destinationQuery.trim().isEmpty) {
      _isDestinationError = true;
      notifyListeners();
      return false;
    }
    _isDestinationError = false;

    _isSearching = true;
    notifyListeners();

    try {
      _searchResults = await _searchService.searchHotels(
        query: _destinationQuery,
        startDate: _selectedDateRange?.start,
        endDate: _selectedDateRange?.end,
        guests: _guestCount,
      );
      _isFromCache = _searchService.isFromCache;
      _hasPerformedSearch = true;
      return true;
    } catch (e) {
      debugPrint('Error searching hotels: $e');
      return false;
    } finally {
      _isSearching = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _connectivitySubscription?.cancel();
    super.dispose();
  }
}
