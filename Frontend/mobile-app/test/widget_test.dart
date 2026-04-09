import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/main.dart';
import 'package:travel_hub/view_models/login_view_model.dart';
import 'package:travel_hub/view_models/register_view_model.dart';
import 'package:travel_hub/view_models/search_view_model.dart';
import 'package:travel_hub/services/connectivity_service.dart';

void main() {
  testWidgets('App starts at home view', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => LoginViewModel()),
          ChangeNotifierProvider(create: (_) => RegisterViewModel()),
          ChangeNotifierProvider(create: (_) => ConnectivityService()),
          ChangeNotifierProxyProvider<ConnectivityService, SearchViewModel>(
            create: (context) => SearchViewModel(
              connectivityService: context.read<ConnectivityService>(),
            ),
            update: (context, connectivity, previous) =>
                previous ?? SearchViewModel(connectivityService: connectivity),
          ),
        ],
        child: const MyApp(),
      ),
    );

    // Verify that we are on the home screen (checks for TravelHub text)
    expect(find.text('TravelHub'), findsOneWidget);
  });
}
