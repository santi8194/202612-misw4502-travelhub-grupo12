import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/reservation.dart';
import 'package:travel_hub/services/booking_service.dart';
import 'package:travel_hub/view_models/reservation_detail_view_model.dart';
import 'package:travel_hub/views/reservation_detail_view.dart';

class MockBookingService extends Mock implements BookingService {}

class MockReservationDetailViewModel extends Mock
    implements ReservationDetailViewModel {}

void main() {
  late MockBookingService mockBookingService;
  late MockReservationDetailViewModel mockVM;
  late Reservation testReservation;

  setUp(() {
    mockBookingService = MockBookingService();
    mockVM = MockReservationDetailViewModel();
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

    when(() => mockVM.isLoading).thenReturn(false);
    when(() => mockVM.reservation).thenReturn(testReservation);
    when(() => mockVM.errorMessage).thenReturn(null);

    when(
      () => mockBookingService.getReservationDetail(any()),
    ).thenAnswer((_) async => testReservation);
  });

  Widget createWidgetUnderTest() {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('es')],
      locale: const Locale('es'),
      home: ReservationDetailView(reservationId: 'res-123', viewModel: mockVM),
    );
  }

  testWidgets('ReservationDetailView renders correctly', (tester) async {
    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pumpAndSettle();

    expect(find.text('CONF123'), findsOneWidget);
    expect(find.text('Test Hotel'), findsOneWidget);
    expect(find.text('Confirmada'), findsOneWidget);

    // Check for buttons
    expect(find.byIcon(Icons.file_download_outlined), findsOneWidget);
    expect(find.text('Descargar Comprobante PDF'), findsOneWidget);
  });
}
