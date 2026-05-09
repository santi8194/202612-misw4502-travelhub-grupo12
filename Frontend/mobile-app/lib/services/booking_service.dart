import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

import '../models/habitacion.dart';
import '../models/reservation.dart';

class BookingService {
  final http.Client _httpClient;

  String get baseUrl {
    try {
      const fromDefine = String.fromEnvironment('BOOKING_API_BASE_URL');
      if (fromDefine.isNotEmpty) return fromDefine;

      final fromEnv = dotenv.env['BOOKING_API_BASE_URL'];
      if (fromEnv != null) return fromEnv;
    } catch (_) {}
    return 'http://10.0.2.2:8081'; // Default base URL for booking service
  }

  String get catalogBaseUrl {
    try {
      const fromDefine = String.fromEnvironment('CATALOG_API_BASE_URL');
      if (fromDefine.isNotEmpty) return fromDefine;

      final fromEnv = dotenv.env['CATALOG_API_BASE_URL'];
      if (fromEnv != null) return fromEnv;
    } catch (_) {}
    return 'http://10.0.2.2:8080'; // Default base URL for catalog service
  }

  String get paymentBaseUrl {
    try {
      const fromDefine = String.fromEnvironment('PAYMENT_API_BASE_URL');
      if (fromDefine.isNotEmpty) return fromDefine;

      final fromEnv = dotenv.env['PAYMENT_API_BASE_URL'];
      if (fromEnv != null) return fromEnv;
    } catch (_) {}
    return 'http://10.0.2.2:8082'; // Default base URL for payment service
  }

  BookingService({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client();

  Future<Reservation> getReservationDetail(String reservationId) async {
    final uri = Uri.parse('$baseUrl/reserva/$reservationId');
    final response = await _httpClient.get(uri);

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return _enrichReservation(data);
    }

    throw Exception(
      'Error al obtener detalle de la reserva ($reservationId): ${response.statusCode}',
    );
  }

  String _resolveStatus(String bookingStatus, String? paymentStatus) {
    if (bookingStatus == 'CONFIRMADA') return 'CONFIRMADA';
    if (bookingStatus == 'CANCELADA') return 'CANCELADA';

    if (bookingStatus == 'HOLD' || bookingStatus == 'PENDIENTE') {
      if (paymentStatus == 'APPROVED') return 'PENDIENTE_CONFIRMACION_HOTEL';
      return 'PENDIENTE_PAGO';
    }

    return 'CANCELADA';
  }

  Future<Map<String, dynamic>?> _getCategory(String categoryId) async {
    try {
      final uri = Uri.parse('$catalogBaseUrl/categories/$categoryId');
      final response = await _httpClient.get(uri);
      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }

  Future<Map<String, dynamic>?> _getPaymentInfo(String reservationId) async {
    try {
      final uri = Uri.parse(
        '$paymentBaseUrl/payments/by-reserva/$reservationId',
      );
      final response = await _httpClient.get(uri);
      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }

  Future<double?> _calculatePrice(
    String categoryId,
    String checkIn,
    String checkOut,
  ) async {
    try {
      final uri = Uri.parse('$catalogBaseUrl/calculate-room-price');
      final response = await _httpClient.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'id_categoria': categoryId,
          'fecha_inicio': checkIn,
          'fecha_fin': checkOut,
          'pais_usuario': 'CO', // Default to CO if unknown
        }),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;
        return (data['total'] as num?)?.toDouble();
      }
    } catch (_) {}
    return null;
  }

  Future<Reservation> _enrichReservation(Map<String, dynamic> booking) async {
    final reservationId = booking['id_reserva'] as String;
    final categoryId = booking['id_categoria'] as String;

    final results = await Future.wait([
      _getCategory(categoryId),
      _getPaymentInfo(reservationId),
    ]);

    final category = results[0] as Map<String, dynamic>?;
    final payment = results[1] as Map<String, dynamic>?;

    final paymentStatus = payment?['estado'] as String?;
    double? price = (payment?['monto'] as num?)?.toDouble();

    if (paymentStatus != 'APPROVED') {
      final calculatedPrice = await _calculatePrice(
        categoryId,
        booking['fecha_check_in'] as String,
        booking['fecha_check_out'] as String,
      );
      if (calculatedPrice != null) {
        price = calculatedPrice;
      }
    }

    final ocupacion = booking['ocupacion'] as Map<String, dynamic>? ?? {};
    final guestCount =
        (ocupacion['adultos'] as int? ?? 0) +
        (ocupacion['ninos'] as int? ?? 0) +
        (ocupacion['infantes'] as int? ?? 0);

    return Reservation(
      id: reservationId,
      hotelName: category?['nombre_comercial'] as String? ?? '—',
      confirmationCode:
          (booking['codigo_confirmacion_ota'] as String?) ??
          (booking['codigo_localizador_pms'] as String?) ??
          '',
      guestCount: guestCount,
      dateRange: DateTimeRange(
        start: DateTime.parse(booking['fecha_check_in'] as String),
        end: DateTime.parse(booking['fecha_check_out'] as String),
      ),
      status: _resolveStatus(booking['estado'] as String, paymentStatus),
      room: Habitacion(
        title: category?['nombre_comercial'] as String? ?? 'Habitación',
        location:
            '', // Catalog doesn't provide this in the category list endpoint
        imageUrl:
            category?['foto_portada_url'] as String? ??
            'https://via.placeholder.com/150',
        price: price ?? 0.0,
        amenities: [],
      ),
    );
  }

  Future<List<Reservation>> getUserReservations(String userId) async {
    try {
      final uri = Uri.parse('$baseUrl/reserva/usuario/$userId');
      final response = await _httpClient.get(uri);

      if (response.statusCode == 200) {
        final List<dynamic> bookings = json.decode(response.body);
        final enrichedReservations = await Future.wait(
          bookings.map((b) => _enrichReservation(b as Map<String, dynamic>)),
        );
        return enrichedReservations;
      }
    } catch (_) {}
    return [];
  }
}
