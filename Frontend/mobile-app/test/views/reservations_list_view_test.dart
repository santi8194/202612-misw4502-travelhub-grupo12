import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/models/habitacion.dart';
import 'package:travel_hub/models/reservation.dart';
import 'package:travel_hub/services/booking_service.dart';
import 'package:travel_hub/services/user_service.dart';
import 'package:travel_hub/view_models/reservations_list_view_model.dart';
import 'package:travel_hub/views/reservations_list_view.dart';

class MockReservationsListViewModel extends Mock
    implements ReservationsListViewModel {}

class MockUserService extends Mock implements UserService {}

class MockBookingService extends Mock implements BookingService {}

void main() {
  late MockReservationsListViewModel mockVM;
  late MockUserService mockUserService;
  late MockBookingService mockBookingService;
  late List<Reservation> upcoming;

  setUp(() {
    mockVM = MockReservationsListViewModel();
    mockUserService = MockUserService();
    mockBookingService = MockBookingService();
    upcoming = [
      Reservation(
        id: 'res-1',
        hotelName: 'Upcoming Hotel',
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
    ];

    when(() => mockVM.isLoading).thenReturn(false);
    when(() => mockVM.upcomingReservations).thenReturn(upcoming);
    when(() => mockVM.pastReservations).thenReturn([]);
    when(() => mockVM.reservations).thenReturn(upcoming);
    when(() => mockVM.errorMessage).thenReturn(null);
    when(() => mockVM.isOffline).thenReturn(false);
    when(() => mockUserService.getUserId()).thenAnswer((_) async => 'user-123');
    when(() => mockVM.loadReservations(any())).thenAnswer((_) async => {});
  });

  Widget createWidgetUnderTest() {
    return MultiProvider(
      providers: [
        Provider<UserService>.value(value: mockUserService),
        Provider<BookingService>.value(value: mockBookingService),
        ChangeNotifierProvider<ReservationsListViewModel>.value(value: mockVM),
      ],
      child: const MaterialApp(
        localizationsDelegates: [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: [Locale('en'), Locale('es')],
        locale: Locale('es'),
        home: ReservationsListView(),
      ),
    );
  }

  testWidgets('ReservationsListView renders lists correctly', (tester) async {
    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    expect(find.text('Mis Reservas'), findsOneWidget);
    expect(find.text('Upcoming Hotel'), findsOneWidget);
    expect(find.text('PRÓXIMAS RESERVAS'), findsOneWidget);
  });

  testWidgets('ReservationsListView shows empty state', (tester) async {
    when(() => mockVM.upcomingReservations).thenReturn([]);
    when(() => mockVM.pastReservations).thenReturn([]);
    when(() => mockVM.reservations).thenReturn([]);

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    expect(find.textContaining('próximas reservas'), findsOneWidget);
    expect(find.textContaining('reservas pasadas'), findsOneWidget);
  });

  testWidgets('ReservationsListView shows offline warning', (tester) async {
    when(() => mockVM.isOffline).thenReturn(true);

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    expect(find.textContaining('sin conexión'), findsOneWidget);
  });

  testWidgets('ReservationsListView shows loading skeleton', (tester) async {
    when(() => mockVM.isLoading).thenReturn(true);
    when(() => mockVM.upcomingReservations).thenReturn([]);
    when(() => mockVM.reservations).thenReturn([]);

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    // The skeleton should be present
    expect(
      find.byType(CustomScrollView),
      findsWidgets,
    ); // Skeleton uses custom scroll view
    expect(find.textContaining('Mis Reservas'), findsWidgets); // Used in header
  });

  testWidgets('ReservationsListView pull to refresh', (tester) async {
    when(() => mockVM.upcomingReservations).thenReturn([]);
    when(() => mockVM.pastReservations).thenReturn([]);

    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    await tester.fling(find.text('Mis Reservas'), const Offset(0, 300), 1000);
    await tester.pumpAndSettle();

    verify(() => mockVM.loadReservations(any())).called(greaterThan(0));
  });

  testWidgets('ReservationsListView tap navigates to detail', (tester) async {
    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    await tester.tap(find.text('Upcoming Hotel'));
    await tester.pumpAndSettle();

    expect(
      find.text('Upcoming Hotel'),
      findsNothing,
    ); // Navigated away, or new view rendered
  });
}
