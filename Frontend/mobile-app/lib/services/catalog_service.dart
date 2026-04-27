import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

import '../models/categoria_habitacion.dart';

class RoomPriceCalculation {
  final double pricePerNight;
  final int nights;
  final double subtotal;
  final double taxesAndCharges;
  final double total;
  final String currency;
  final String currencySymbol;
  final String? tariffType;
  final String? taxName;

  const RoomPriceCalculation({
    required this.pricePerNight,
    required this.nights,
    required this.subtotal,
    required this.taxesAndCharges,
    required this.total,
    required this.currency,
    required this.currencySymbol,
    this.tariffType,
    this.taxName,
  });

  factory RoomPriceCalculation.fromJson(Map<String, dynamic> json) {
    return RoomPriceCalculation(
      pricePerNight: (json['precio_por_noche'] as num?)?.toDouble() ?? 0.0,
      nights: (json['noches'] as num?)?.toInt() ?? 0,
      subtotal: (json['subtotal'] as num?)?.toDouble() ?? 0.0,
      taxesAndCharges: (json['impuestos_y_cargos'] as num?)?.toDouble() ?? 0.0,
      total: (json['total'] as num?)?.toDouble() ?? 0.0,
      currency: (json['moneda'] as String?) ?? 'USD',
      currencySymbol: (json['simbolo_moneda'] as String?) ?? r'$',
      tariffType: json['tipo_tarifa'] as String?,
      taxName: json['impuesto_nombre'] as String?,
    );
  }
}

class CatalogService {
  final http.Client _httpClient;

  String get baseUrl {
    try {
      const fromDefine = String.fromEnvironment('CATALOG_API_BASE_URL');
      if (fromDefine.isNotEmpty) return fromDefine;

      final fromEnv = dotenv.env['CATALOG_API_BASE_URL'];
      if (fromEnv != null) return fromEnv;
    } catch (_) {}
    return 'http://10.0.2.2:8001';
  }

  CatalogService({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client();

  Future<CategoriaHabitacion> getCategoria(String categoryId) async {
    final uri = Uri.parse('$baseUrl/catalog/categories/$categoryId');
    final response = await _httpClient.get(uri);

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return CategoriaHabitacion.fromJson(data);
    }

    throw Exception(
      'Error al obtener categoría ($categoryId): ${response.statusCode}',
    );
  }

  Future<CategoriaPricing> getCategoryPricing({
    required String propertyId,
    required String categoryId,
  }) async {
    final uri = Uri.parse(
      '$baseUrl/catalog/properties/$propertyId/categories/$categoryId/pricing',
    );
    print('CatalogService.getCategoryPricing URI: $uri');
    final response = await _httpClient
        .get(uri)
        .timeout(const Duration(seconds: 8));
    print('CatalogService.getCategoryPricing status: \${response.statusCode}');

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return CategoriaPricing.fromJson(data);
    }

    throw Exception(
      'Error al obtener pricing ($propertyId/$categoryId): \${response.statusCode}',
    );
  }

  Future<String?> getPropertyIdByCategory(String categoryId) async {
    final uri = Uri.parse(
      '$baseUrl/catalog/properties/by-category/$categoryId',
    );
    final response = await _httpClient
        .get(uri)
        .timeout(const Duration(seconds: 8));

    if (response.statusCode != 200) return null;

    final data = json.decode(response.body) as Map<String, dynamic>;
    final id = data['id_propiedad'] as String?;
    if (id == null || id.isEmpty) return null;
    return id;
  }

  Future<RoomPriceCalculation> calculateRoomPrice({
    required String categoryId,
    required DateTime startDate,
    required DateTime endDate,
    required String userCountry,
  }) async {
    final uri = Uri.parse('$baseUrl/catalog/calculate-room-price');
    final response = await _httpClient
        .post(
          uri,
          headers: const {'Content-Type': 'application/json'},
          body: jsonEncode({
            'id_categoria': categoryId,
            'fecha_inicio': startDate.toIso8601String().split('T').first,
            'fecha_fin': endDate.toIso8601String().split('T').first,
            'pais_usuario': userCountry,
          }),
        )
        .timeout(const Duration(seconds: 8));

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return RoomPriceCalculation.fromJson(data);
    }

    throw Exception(
      'Error al calcular precio de habitación ($categoryId): ${response.statusCode}',
    );
  }
}
