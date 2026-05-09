import 'package:flutter/material.dart';

import '../models/reservation.dart';
import '../services/booking_service.dart';
import '../services/connectivity_service.dart';

class ReservationsListViewModel extends ChangeNotifier {
  final BookingService _bookingService;
  final ConnectivityService _connectivityService;

  List<Reservation> _reservations = [];
  bool _isLoading = false;
  String? _errorMessage;
  bool _isOffline = false;

  ReservationsListViewModel({
    required BookingService bookingService,
    required ConnectivityService connectivityService,
  }) : _bookingService = bookingService,
       _connectivityService = connectivityService;

  List<Reservation> get reservations => _reservations;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isOffline => _isOffline;

  List<Reservation> get upcomingReservations {
    final now = DateTime.now();
    return _reservations
        .where(
          (r) =>
              r.dateRange.start.isAfter(now) ||
              r.dateRange.start.isAtSameMomentAs(now),
        )
        .toList()
      ..sort((a, b) => a.dateRange.start.compareTo(b.dateRange.start));
  }

  List<Reservation> get pastReservations {
    final now = DateTime.now();
    return _reservations.where((r) => r.dateRange.start.isBefore(now)).toList()
      ..sort((a, b) => b.dateRange.start.compareTo(a.dateRange.start));
  }

  Future<void> loadReservations(String userId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _isOffline = !_connectivityService.isOnline;

      // En una implementación real, aquí se manejaría la caché si está offline.
      // Por ahora, el servicio siempre devuelve datos dummy.
      _reservations = await _bookingService.getUserReservations(userId);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
