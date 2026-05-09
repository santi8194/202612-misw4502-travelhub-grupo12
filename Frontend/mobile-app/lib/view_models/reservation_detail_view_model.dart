import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/reservation.dart';
import '../services/booking_service.dart';

class ReservationDetailViewModel extends ChangeNotifier {
  final String reservationId;
  final BookingService _bookingService;

  Reservation? _reservation;
  bool _isLoading = false;
  String? _errorMessage;

  ReservationDetailViewModel({
    required this.reservationId,
    BookingService? bookingService,
    Reservation? initialReservation,
  }) : _bookingService = bookingService ?? BookingService(),
       _reservation = initialReservation {
    if (_reservation == null) {
      loadReservation();
    }
  }

  Reservation? get reservation => _reservation;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> loadReservation() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _reservation = await _bookingService.getReservationDetail(reservationId);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> callHotel() async {
    final phone = _reservation?.hotelPhone;
    if (phone == null || phone.isEmpty) return;

    final Uri url = Uri.parse('tel:$phone');
    if (await canLaunchUrl(url)) {
      await launchUrl(url);
    }
  }

  Future<void> openInMaps() async {
    final address = _reservation?.hotelAddress;
    if (address == null || address.isEmpty) return;

    final query = Uri.encodeComponent(address);
    final Uri url = Uri.parse(
      'https://www.google.com/maps/search/?api=1&query=$query',
    );
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  Future<void> shareReservation() async {
    final res = _reservation;
    if (res == null) return;

    final text =
        'Reserva en ${res.hotelName}\n'
        'Código: ${res.confirmationCode}\n'
        'Check-in: ${res.dateRange.start.day}/${res.dateRange.start.month}/${res.dateRange.start.year}\n'
        'Dirección: ${res.hotelAddress}';

    await Share.share(text);
  }
}
