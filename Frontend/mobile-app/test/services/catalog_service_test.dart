import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:travel_hub/services/catalog_service.dart';

class MockHttpClient extends Mock implements http.Client {}

void main() {
  late MockHttpClient mockHttpClient;
  late CatalogService service;

  setUpAll(() {
    registerFallbackValue(Uri());
  });

  setUp(() {
    mockHttpClient = MockHttpClient();
    service = CatalogService(httpClient: mockHttpClient);
  });

  test('getCategoria returns parsed category on 200 response', () async {
    when(() => mockHttpClient.get(any())).thenAnswer(
      (_) async => http.Response(
        jsonEncode({
          'id_categoria': 'cat-1',
          'codigo_mapeo_pms': 'PMS-001',
          'nombre_comercial': 'Suite Deluxe',
          'descripcion': 'Ocean view suite',
          'precio_base': {
            'monto': '100.00',
            'moneda': 'USD',
            'cargo_servicio': '15.00',
          },
          'foto_portada_url': 'https://example.com/room.jpg',
          'capacidad_pax': 2,
          'politica_cancelacion': {
            'dias_anticipacion': 3,
            'porcentaje_penalidad': '20.00',
          },
        }),
        200,
      ),
    );

    final categoria = await service.getCategoria('cat-1');

    expect(categoria.idCategoria, 'cat-1');
    expect(categoria.nombreComercial, 'Suite Deluxe');
    expect(categoria.precioBase.moneda, 'USD');
    verify(
      () => mockHttpClient.get(
        Uri.parse('${service.baseUrl}/catalog/categories/cat-1'),
      ),
    ).called(1);
  });

  test('getCategoria throws on non-200 response', () async {
    when(
      () => mockHttpClient.get(any()),
    ).thenAnswer((_) async => http.Response('not found', 404));

    await expectLater(
      () => service.getCategoria('missing-category'),
      throwsA(
        isA<Exception>().having(
          (error) => error.toString(),
          'message',
          contains('404'),
        ),
      ),
    );
  });

  test('calculateRoomPrice returns parsed breakdown on 200 response', () async {
    when(
      () => mockHttpClient.post(
        any(),
        headers: any(named: 'headers'),
        body: any(named: 'body'),
      ),
    ).thenAnswer(
      (_) async => http.Response(
        jsonEncode({
          'precio_por_noche': 150000.0,
          'noches': 2,
          'subtotal': 300000.0,
          'impuestos_y_cargos': 57000.0,
          'total': 357000.0,
          'moneda': 'COP',
          'simbolo_moneda': r'$',
          'tipo_tarifa': 'BASE',
          'impuesto_nombre': 'IVA',
        }),
        200,
      ),
    );

    final result = await service.calculateRoomPrice(
      categoryId: 'cat-1',
      startDate: DateTime(2026, 4, 22),
      endDate: DateTime(2026, 4, 24),
      userCountry: 'Colombia',
    );

    expect(result.pricePerNight, 150000.0);
    expect(result.nights, 2);
    expect(result.total, 357000.0);
    expect(result.currency, 'COP');
    expect(result.taxName, 'IVA');
    verify(
      () => mockHttpClient.post(
        Uri.parse('${service.baseUrl}/catalog/calculate-room-price'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'id_categoria': 'cat-1',
          'fecha_inicio': '2026-04-22',
          'fecha_fin': '2026-04-24',
          'pais_usuario': 'Colombia',
        }),
      ),
    ).called(1);
  });

  test('calculateRoomPrice throws on non-200 response', () async {
    when(
      () => mockHttpClient.post(
        any(),
        headers: any(named: 'headers'),
        body: any(named: 'body'),
      ),
    ).thenAnswer((_) async => http.Response('error', 500));

    await expectLater(
      () => service.calculateRoomPrice(
        categoryId: 'cat-1',
        startDate: DateTime(2026, 4, 22),
        endDate: DateTime(2026, 4, 24),
        userCountry: 'Colombia',
      ),
      throwsA(
        isA<Exception>().having(
          (error) => error.toString(),
          'message',
          contains('500'),
        ),
      ),
    );
  });
}
