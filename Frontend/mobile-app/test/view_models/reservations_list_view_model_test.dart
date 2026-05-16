import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/reservation.dart';
import 'package:travel_hub/services/booking_service.dart';
import 'package:travel_hub/services/connectivity_service.dart';
import 'package:travel_hub/view_models/reservations_list_view_model.dart';

class MockBookingService extends Mock implements BookingService {}

class MockConnectivityService extends Mock implements ConnectivityService {}

void main() {
  late MockBookingService mockBookingService;
  late MockConnectivityService mockConnectivity;
  late List<Reservation> testReservations;

  setUp(() {
    mockBookingService = MockBookingService();
    mockConnectivity = MockConnectivityService();
    when(() => mockConnectivity.isOnline).thenReturn(true);
    when(
      () => mockConnectivity.onConnectivityChanged,
    ).thenAnswer((_) => const Stream.empty());
    testReservations = [
      Reservation(
        id: 'res-1',
        hotelName: 'Hotel 1',
        confirmationCode: 'CONF1',
        guestCount: 2,
        dateRange: DateTimeRange(
          start: DateTime.now().add(const Duration(days: 5)),
          end: DateTime.now().add(const Duration(days: 7)),
        ),
        status: 'CONFIRMADA',
        room: Habitacion(
          title: 'Room 1',
          location: 'Loc 1',
          imageUrl: 'url1',
          price: 100,
          amenities: [],
        ),
      ),
      Reservation(
        id: 'res-2',
        hotelName: 'Hotel 2',
        confirmationCode: 'CONF2',
        guestCount: 1,
        dateRange: DateTimeRange(
          start: DateTime.now().subtract(const Duration(days: 10)),
          end: DateTime.now().subtract(const Duration(days: 8)),
        ),
        status: 'CONFIRMADA',
        room: Habitacion(
          title: 'Room 2',
          location: 'Loc 2',
          imageUrl: 'url2',
          price: 200,
          amenities: [],
        ),
      ),
    ];
  });

  group('ReservationsListViewModel Tests', () {
    test('loadReservations populates upcoming and past lists', () async {
      when(
        () => mockBookingService.getUserReservations(any()),
      ).thenAnswer((_) async => testReservations);

      final viewModel = ReservationsListViewModel(
        bookingService: mockBookingService,
        connectivityService: mockConnectivity,
      );

      await viewModel.loadReservations('user-123');

      expect(viewModel.isLoading, false);
      expect(viewModel.upcomingReservations.length, 1);
      expect(viewModel.pastReservations.length, 1);
      expect(viewModel.upcomingReservations.first.id, 'res-1');
      expect(viewModel.pastReservations.first.id, 'res-2');
    });

    test('loadReservations handles error', () async {
      when(
        () => mockBookingService.getUserReservations(any()),
      ).thenThrow(Exception('API Error'));

      final viewModel = ReservationsListViewModel(
        bookingService: mockBookingService,
        connectivityService: mockConnectivity,
      );

      await viewModel.loadReservations('user-123');

      expect(viewModel.isLoading, false);
      expect(viewModel.errorMessage, contains('API Error'));
      expect(viewModel.upcomingReservations, isEmpty);
    });
  });
}
