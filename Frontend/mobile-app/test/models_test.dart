import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/models/categoria_habitacion.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/location_suggestion.dart';

void main() {
  group('Models Tests', () {
    test('Hotel.fromJson creates a valid object', () {
      final json = {
        'imageUrl': 'test.jpg',
        'title': 'Test Hotel',
        'location': 'Test City',
        'amenities': ['Wifi', 'Pool'],
        'isSpecialOffer': true,
      };

      final hotel = Habitacion.fromJson(json);

      expect(hotel.imageUrl, 'test.jpg');
      expect(hotel.title, 'Test Hotel');
      expect(hotel.location, 'Test City');
      expect(hotel.amenities, ['Wifi', 'Pool']);
      expect(hotel.isSpecialOffer, true);
    });

    test('Hotel.toJson returns a valid map', () {
      final hotel = Habitacion(
        imageUrl: 'test.jpg',
        title: 'Test Hotel',
        location: 'Test City',
        amenities: ['Wifi'],
        isSpecialOffer: false,
        price: 99.0,
      );

      final json = hotel.toJson();

      expect(json['imageUrl'], 'test.jpg');
      expect(json['title'], 'Test Hotel');
      expect(json['location'], 'Test City');
      expect(json['amenities'], ['Wifi']);
      expect(json['isSpecialOffer'], false);
      expect(json['price'], 99.0);
    });

    test('LocationSuggestion properties and methods', () {
      const suggestion = LocationSuggestion(
        ciudad: 'Bogota',
        estadoProvincia: 'Cundinamarca',
        pais: 'Colombia',
      );

      expect(suggestion.displayName, 'Bogota, Cundinamarca, Colombia');
      expect(suggestion.toString(), 'Bogota, Cundinamarca, Colombia');

      final json = suggestion.toJson();
      expect(json['ciudad'], 'Bogota');

      final fromJson = LocationSuggestion.fromJson(json);
      expect(fromJson.ciudad, 'Bogota');
    });

    test('CategoriaHabitacion.fromJson creates a nested category model', () {
      final json = {
        'id_categoria': 'cat-1',
        'codigo_mapeo_pms': 'PMS-001',
        'nombre_comercial': 'Suite Deluxe',
        'descripcion': 'Ocean view suite',
        'precio_base': {
          'monto': '250.00',
          'moneda': 'USD',
          'cargo_servicio': '35.00',
        },
        'foto_portada_url': 'https://example.com/room.jpg',
        'capacidad_pax': 3,
        'politica_cancelacion': {
          'dias_anticipacion': 5,
          'porcentaje_penalidad': '20.00',
        },
      };

      final categoria = CategoriaHabitacion.fromJson(json);

      expect(categoria.idCategoria, 'cat-1');
      expect(categoria.codigoMapeoPms, 'PMS-001');
      expect(categoria.nombreComercial, 'Suite Deluxe');
      expect(categoria.precioBase.monto, '250.00');
      expect(categoria.precioBase.moneda, 'USD');
      expect(categoria.precioBase.cargoServicio, '35.00');
      expect(categoria.capacidadPax, 3);
      expect(categoria.politicaCancelacion.diasAnticipacion, 5);
      expect(categoria.politicaCancelacion.porcentajePenalidad, '20.00');
    });

    test(
      'CategoriaHabitacion.fromJson uses nested defaults for missing data',
      () {
        final categoria = CategoriaHabitacion.fromJson({});

        expect(categoria.idCategoria, '');
        expect(categoria.codigoMapeoPms, '');
        expect(categoria.nombreComercial, '');
        expect(categoria.descripcion, '');
        expect(categoria.fotoPortadaUrl, '');
        expect(categoria.capacidadPax, 0);
        expect(categoria.precioBase.monto, '0.00');
        expect(categoria.precioBase.moneda, '');
        expect(categoria.precioBase.cargoServicio, '0.00');
        expect(categoria.politicaCancelacion.diasAnticipacion, 0);
        expect(categoria.politicaCancelacion.porcentajePenalidad, '0.00');
      },
    );

    test(
      'CategoriaHabitacion.toJson returns the serialized payload string',
      () {
        const categoria = CategoriaHabitacion(
          idCategoria: 'cat-2',
          codigoMapeoPms: 'PMS-002',
          nombreComercial: 'Family Room',
          descripcion: 'Large room for families',
          precioBase: PrecioBase(
            monto: '180.00',
            moneda: 'COP',
            cargoServicio: '20.00',
          ),
          fotoPortadaUrl: 'https://example.com/family-room.jpg',
          capacidadPax: 4,
          politicaCancelacion: PoliticaCancelacion(
            diasAnticipacion: 2,
            porcentajePenalidad: '10.00',
          ),
        );

        final json = categoria.toJson();

        expect(json, contains('"id_categoria": "cat-2"'));
        expect(json, contains('"codigo_mapeo_pms": "PMS-002"'));
        expect(json, contains('"monto": "180.00"'));
        expect(json, contains('"cargo_servicio": "20.00"'));
        expect(json, contains('"dias_anticipacion": 2'));
        expect(json, contains('"porcentaje_penalidad": "10.00"'));
      },
    );
  });
}
