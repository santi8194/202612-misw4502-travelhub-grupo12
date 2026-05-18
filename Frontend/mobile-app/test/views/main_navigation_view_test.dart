import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/services/booking_service.dart';
import 'package:travel_hub/services/connectivity_service.dart';
import 'package:travel_hub/services/user_service.dart';
import 'package:travel_hub/view_models/notifications_view_model.dart';
import 'package:travel_hub/view_models/reservations_list_view_model.dart';
import 'package:travel_hub/view_models/search_view_model.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';
import 'package:travel_hub/views/main_navigation_view.dart';

class MockSearchViewModel extends Mock implements SearchViewModel {}

class MockReservationsListViewModel extends Mock
    implements ReservationsListViewModel {}

class MockConnectivityService extends Mock implements ConnectivityService {}

class MockNotificationsViewModel extends Mock
    implements NotificationsViewModel {}

class MockUserService extends Mock implements UserService {}

class MockBookingService extends Mock implements BookingService {}

void main() {
  setUpAll(() {
    registerFallbackValue(DateTime.now());
  });

  testWidgets('MainNavigationView renders and switches tabs', (
    WidgetTester tester,
  ) async {
    final mockSearchVM = MockSearchViewModel();
    final mockReservationsVM = MockReservationsListViewModel();
    final mockConnectivity = MockConnectivityService();
    final mockNotificationsVM = MockNotificationsViewModel();
    final mockUserService = MockUserService();
    final mockBookingService = MockBookingService();

    when(() => mockNotificationsVM.unreadCount).thenReturn(0);
    when(() => mockUserService.getUserId()).thenAnswer((_) async => 'user-123');
    when(() => mockSearchVM.destinationQuery).thenReturn('');
    when(() => mockSearchVM.selectedDateRange).thenReturn(null);
    when(() => mockSearchVM.guestCount).thenReturn(2);
    when(() => mockSearchVM.isSearching).thenReturn(false);
    when(() => mockSearchVM.hasNoResults).thenReturn(false);
    when(() => mockSearchVM.isFromCache).thenReturn(false);
    when(() => mockSearchVM.searchResults).thenReturn([]);
    when(() => mockSearchVM.isDestinationError).thenReturn(false);
    when(() => mockSearchVM.isOffline).thenReturn(false);

    when(() => mockReservationsVM.isLoading).thenReturn(false);
    when(() => mockReservationsVM.upcomingReservations).thenReturn([]);
    when(() => mockReservationsVM.pastReservations).thenReturn([]);
    when(() => mockReservationsVM.errorMessage).thenReturn(null);
    when(() => mockReservationsVM.isOffline).thenReturn(false);
    when(
      () => mockReservationsVM.loadReservations(any()),
    ).thenAnswer((_) async => {});

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider<ConnectivityService>.value(
            value: mockConnectivity,
          ),
          ChangeNotifierProvider<SearchViewModel>.value(value: mockSearchVM),
          ChangeNotifierProvider<ReservationsListViewModel>.value(
            value: mockReservationsVM,
          ),
          ChangeNotifierProvider<UserPreferencesViewModel>(
            create: (_) => UserPreferencesViewModel(),
          ),
          ChangeNotifierProvider<NotificationsViewModel>.value(
            value: mockNotificationsVM,
          ),
          Provider<UserService>.value(value: mockUserService),
          Provider<BookingService>.value(value: mockBookingService),
        ],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: [Locale('en'), Locale('es')],
          home: MainNavigationView(),
        ),
      ),
    );

    expect(find.byType(BottomNavigationBar), findsOneWidget);

    // Tap mis reservas (index 1)
    await tester.tap(find.byIcon(Icons.card_travel));
    await tester.pumpAndSettle();

    // Tap perfil (index 2)
    await tester.tap(find.byIcon(Icons.person_outline));
    await tester.pumpAndSettle();

    // Verify profile text is shown (both in BottomNavigationBar and center of screen)
    expect(find.text('Profile'), findsAtLeast(1));

    // Back to search (index 0)
    await tester.tap(
      find.descendant(
        of: find.byType(BottomNavigationBar),
        matching: find.byIcon(Icons.search),
      ),
    );
    await tester.pumpAndSettle();
  });
}
