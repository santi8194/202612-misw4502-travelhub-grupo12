import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

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

  BookingService({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client();

  Future<Reservation> getReservationDetail(String reservationId) async {
    final uri = Uri.parse('$baseUrl/reserva/$reservationId');
    final response = await _httpClient.get(uri);

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return Reservation.fromJson(data);
    }

    throw Exception(
      'Error al obtener detalle de la reserva ($reservationId): ${response.statusCode}',
    );
  }
}
