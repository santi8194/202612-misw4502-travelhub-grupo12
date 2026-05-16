import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/models/categoria_habitacion.dart';
import 'package:travel_hub/models/country_tax.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/location_suggestion.dart';
import 'package:travel_hub/models/resena.dart';
import 'package:travel_hub/models/reservation.dart';

void main() {
  group('Models Tests', () {
    test('Habitacion fromJson/toJson', () {
      final json = {
        'imageUrl': 'test.jpg',
        'title': 'Test Hotel',
        'location': 'Test City',
        'amenities': ['Wifi'],
        'isSpecialOffer': true,
        'price': 100.0,
      };

      final hotel = Habitacion.fromJson(json);
      expect(hotel.title, 'Test Hotel');
      expect(hotel.toJson()['price'], 100.0);
    });

    test('LocationSuggestion properties', () {
      const suggestion = LocationSuggestion(
        ciudad: 'Bogota',
        estadoProvincia: 'Cundinamarca',
        pais: 'Colombia',
      );
      expect(suggestion.displayName, contains('Bogota'));
      expect(suggestion.toJson()['ciudad'], 'Bogota');
      expect(suggestion.toString(), contains('Bogota'));

      final fromJson = LocationSuggestion.fromJson({
        'ciudad': 'C',
        'estado_provincia': 'S',
        'pais': 'P',
      });
      expect(fromJson.ciudad, 'C');
    });

    test('CategoriaHabitacion full coverage', () {
      final json = {
        'id_categoria': 'c1',
        'precio_base': {'monto': '10', 'moneda': 'USD', 'cargo_servico': '1'},
        'politica_cancelacion': {
          'dias_anticipacion': 1,
          'porcentaje_penalidad': '5',
        },
      };
      final cat = CategoriaHabitacion.fromJson(json);
      expect(cat.idCategoria, 'c1');
      expect(cat.precioBase.monto, '10');

      final emptyCat = CategoriaHabitacion.fromJson({});
      expect(emptyCat.idCategoria, '');

      final toJson = cat.toJson();
      expect(toJson, contains('c1'));
    });

    test('Resena fromJson', () {
      final resena = Resena.fromJson({
        'userName': 'U',
        'rating': 4.5,
        'comment': 'C',
        'date': 'D',
        'userImageUrl': 'I',
      });
      expect(resena.userName, 'U');
      expect(resena.rating, 4.5);

      final emptyResena = Resena.fromJson({});
      expect(emptyResena.userName, '');
    });

    test('Reservation full coverage', () {
      final room = Habitacion(
        title: 'T',
        location: 'L',
        imageUrl: 'I',
        price: 100,
        amenities: [],
      );
      final range = DateTimeRange(
        start: DateTime(2026, 1, 1),
        end: DateTime(2026, 1, 2),
      );

      final res = Reservation(
        id: '1',
        room: room,
        dateRange: range,
        guestCount: 2,
        hotelName: 'Hotel',
        hotelAddress: 'Address',
        hotelPhone: '123',
      );

      expect(res.id, '1');
      expect(res.hotelPhone, '123');

      final json = res.toJson();
      expect(json['id'], '1');

      final fromJson = Reservation.fromJson(json);
      expect(fromJson.id, '1');
      expect(fromJson.hotelName, 'Hotel');

      final copied = res.copyWith(id: '2');
      expect(copied.id, '2');
      expect(copied.hotelName, 'Hotel');
    });

    test('CountryTax and TaxInfo', () {
      const taxInfo = TaxInfo(name: 'IVA', rate: 0.19, note: {'es': 'N'});
      expect(taxInfo.noteForLanguage('es'), 'N');
      expect(taxInfo.noteForLanguage('en'), 'N');

      const countryTax = CountryTax(
        currency: 'COP',
        currencySymbol: r'$',
        locale: 'es_CO',
        decimals: 0,
        usdRate: 4000,
        tax: taxInfo,
      );
      expect(countryTax.currency, 'COP');
    });
  });
}
