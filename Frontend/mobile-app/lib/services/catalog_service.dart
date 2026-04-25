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
    return 'http://10.0.2.2:8080';
  }

  CatalogService({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client();

  Future<CategoriaHabitacion> getCategoria(String categoryId) async {
    final uri = Uri.parse('$baseUrl/categories/$categoryId');
    final response = await _httpClient.get(uri);

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return CategoriaHabitacion.fromJson(data);
    }

    throw Exception(
      'Error al obtener categoría ($categoryId): ${response.statusCode}',
    );
  }

  Future<Map<String, dynamic>> getPropertyDetail(String categoryId) async {
    final uri = Uri.parse('$baseUrl/categories/$categoryId/view-detail');
    final response = await _httpClient.get(uri);

    if (response.statusCode == 200) {
      return json.decode(response.body) as Map<String, dynamic>;
    }

    throw Exception(
      'Error al obtener detalle de propiedad ($categoryId): ${response.statusCode}',
    );
  }
}
