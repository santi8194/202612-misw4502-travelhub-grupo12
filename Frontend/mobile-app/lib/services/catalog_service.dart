import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

import '../models/categoria_habitacion.dart';

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
}
