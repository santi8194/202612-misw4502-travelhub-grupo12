import 'package:flutter_test/flutter_test.dart';
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
      );

      final json = hotel.toJson();

      expect(json['imageUrl'], 'test.jpg');
      expect(json['title'], 'Test Hotel');
      expect(json['location'], 'Test City');
      expect(json['amenities'], ['Wifi']);
      expect(json['isSpecialOffer'], false);
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
  });
}
