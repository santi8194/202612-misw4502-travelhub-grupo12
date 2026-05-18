import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/main.dart';
import 'package:travel_hub/services/booking_service.dart';
import 'package:travel_hub/services/connectivity_service.dart';
import 'package:travel_hub/services/user_service.dart';
import 'package:travel_hub/view_models/login_view_model.dart';
import 'package:travel_hub/view_models/notifications_view_model.dart';
import 'package:travel_hub/view_models/register_view_model.dart';
import 'package:travel_hub/view_models/reservations_list_view_model.dart';
import 'package:travel_hub/view_models/search_view_model.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';

void main() {
  setUpAll(() async {
    await dotenv.load();
  });
  testWidgets('App starts at home view', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider(create: (_) => UserService()),
          Provider(create: (_) => BookingService()),
          ChangeNotifierProvider(create: (_) => LoginViewModel()),
          ChangeNotifierProvider(create: (_) => RegisterViewModel()),
          ChangeNotifierProvider(create: (_) => ConnectivityService()),
          ChangeNotifierProvider(create: (_) => NotificationsViewModel()),
          ChangeNotifierProvider(create: (_) => UserPreferencesViewModel()),
          ChangeNotifierProxyProvider<ConnectivityService, SearchViewModel>(
            create: (context) => SearchViewModel(
              connectivityService: context.read<ConnectivityService>(),
            ),
            update: (context, connectivity, previous) =>
                previous ?? SearchViewModel(connectivityService: connectivity),
          ),
          ChangeNotifierProxyProvider2<
            BookingService,
            ConnectivityService,
            ReservationsListViewModel
          >(
            create: (context) => ReservationsListViewModel(
              bookingService: context.read<BookingService>(),
              connectivityService: context.read<ConnectivityService>(),
            ),
            update: (context, bookingService, connectivity, previous) =>
                previous ??
                ReservationsListViewModel(
                  bookingService: bookingService,
                  connectivityService: connectivity,
                ),
          ),
        ],
        child: const MyApp(),
      ),
    );

    // Verify that we are on the home screen (checks for TravelHub text)
    expect(find.text('TravelHub'), findsOneWidget);
  });
}
