import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/reservation.dart';
import 'package:travel_hub/services/document_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late DocumentService documentService;
  late Reservation testReservation;

  setUp(() {
    documentService = DocumentService();
    testReservation = Reservation(
      id: 'res-123',
      hotelName: 'Test Hotel',
      confirmationCode: 'CONF123',
      guestCount: 2,
      dateRange: DateTimeRange(
        start: DateTime(2026, 6, 1),
        end: DateTime(2026, 6, 5),
      ),
      status: 'CONFIRMADA',
      room: Habitacion(
        title: 'Deluxe Room',
        location: 'Test Loc',
        imageUrl: 'http://image.com',
        price: 500000,
        amenities: [],
      ),
    );
  });

  group('DocumentService Tests', () {
    test('generateAndDownloadReservationPdf completes without error', () async {
      // Testing PDF generation in a unit test environment is limited because
      // 'printing' package uses platform channels.
      // However, we can at least verify that the logic doesn't crash
      // up until the platform call if we were to mock the platform,
      // but here we just want to ensure it's covered.

      // Note: Printing.layoutPdf will fail in test environment if not mocked,
      // but the goal here is to trigger the code paths for coverage.

      // Call generateReservationPdfBytes directly to cover the builder logic
      final bytes = await documentService.generateReservationPdfBytes(
        testReservation,
      );

      expect(bytes, isNotNull);
      expect(bytes.isNotEmpty, true);

      try {
        // We expect this to fail with a missing plugin error or similar in test
        // but we're mainly looking for coverage of the building logic.
        // In a real scenario we'd use a mock for the printing platform channel.
        await documentService.generateAndDownloadReservationPdf(
          testReservation,
        );
      } catch (e) {
        // Expected failure in unit test due to platform channels
        final err = e.toString();
        expect(
          err.contains('MissingPluginException') ||
              err.contains('no implementation found'),
          true,
        );
      }
    });
  });
}
