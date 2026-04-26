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
}
