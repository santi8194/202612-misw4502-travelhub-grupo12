import 'package:flutter/material.dart';

import '../models/habitacion.dart';
import '../models/reservation.dart';

class ConfirmReservationViewModel extends ChangeNotifier {
  final Habitacion room;
  final DateTimeRange selectedDateRange;
  final int guests;

  bool _isConfirming = false;
  String? _confirmationMessage;

  ConfirmReservationViewModel({
    required this.room,
    required this.selectedDateRange,
    required this.guests,
  });

  bool get isConfirming => _isConfirming;
  String? get confirmationMessage => _confirmationMessage;

  Reservation get reservation => Reservation(
    id: _generateReservationId(),
    room: room,
    dateRange: selectedDateRange,
    guestCount: guests,
  );

  Future<bool> confirmReservation() async {
    if (_isConfirming) return false;

    _isConfirming = true;
    _confirmationMessage = null;
    notifyListeners();

    await Future.delayed(const Duration(milliseconds: 900));

    _confirmationMessage = 'Reserva confirmada: ${reservation.id}';
    _isConfirming = false;
    notifyListeners();

    return true;
  }

  String _generateReservationId() {
    return 'TH-${DateTime.now().millisecondsSinceEpoch}';
  }
}
