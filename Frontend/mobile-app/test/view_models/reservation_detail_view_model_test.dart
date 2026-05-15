import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/reservation.dart';
import 'package:travel_hub/services/booking_service.dart';
import 'package:travel_hub/services/document_service.dart';
import 'package:travel_hub/view_models/reservation_detail_view_model.dart';

class MockBookingService extends Mock implements BookingService {}

class MockDocumentService extends Mock implements DocumentService {}

class FakeReservation extends Fake implements Reservation {}

void main() {
  late MockBookingService mockBookingService;
  late MockDocumentService mockDocumentService;
  late Reservation testReservation;

  setUpAll(() {
    registerFallbackValue(FakeReservation());
  });

  setUp(() {
    mockBookingService = MockBookingService();
    mockDocumentService = MockDocumentService();
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

  group('ReservationDetailViewModel Tests', () {
    test('Initial values and automatic loading', () async {
      when(
        () => mockBookingService.getReservationDetail(any()),
      ).thenAnswer((_) async => testReservation);

      final viewModel = ReservationDetailViewModel(
        reservationId: 'res-123',
        bookingService: mockBookingService,
      );

      expect(viewModel.isLoading, true);
      expect(viewModel.reservation, isNull);

      await Future.delayed(Duration.zero);

      expect(viewModel.isLoading, false);
      expect(viewModel.reservation, equals(testReservation));
      verify(
        () => mockBookingService.getReservationDetail('res-123'),
      ).called(1);
    });

    test('Loading with error', () async {
      when(
        () => mockBookingService.getReservationDetail(any()),
      ).thenThrow(Exception('API Error'));

      final viewModel = ReservationDetailViewModel(
        reservationId: 'res-123',
        bookingService: mockBookingService,
      );

      await Future.delayed(Duration.zero);

      expect(viewModel.isLoading, false);
      expect(viewModel.reservation, isNull);
      expect(viewModel.errorMessage, contains('API Error'));
    });

    test('downloadReservationPdf calls document service', () async {
      when(
        () => mockDocumentService.generateAndDownloadReservationPdf(any()),
      ).thenAnswer((_) async => {});

      final viewModel = ReservationDetailViewModel(
        reservationId: 'res-123',
        bookingService: mockBookingService,
        documentService: mockDocumentService,
        initialReservation: testReservation,
      );

      await viewModel.downloadReservationPdf();

      expect(viewModel.isLoading, false);
      verify(
        () => mockDocumentService.generateAndDownloadReservationPdf(
          testReservation,
        ),
      ).called(1);
    });

    test('downloadReservationPdf handles error', () async {
      when(
        () => mockDocumentService.generateAndDownloadReservationPdf(any()),
      ).thenThrow(Exception('PDF Error'));

      final viewModel = ReservationDetailViewModel(
        reservationId: 'res-123',
        bookingService: mockBookingService,
        documentService: mockDocumentService,
        initialReservation: testReservation,
      );

      await viewModel.downloadReservationPdf();

      expect(viewModel.isLoading, false);
      expect(viewModel.errorMessage, contains('PDF Error'));
    });
  });
}
