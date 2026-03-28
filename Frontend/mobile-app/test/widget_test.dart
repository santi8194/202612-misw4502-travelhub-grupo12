import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/main.dart';
import 'package:travel_hub/view_models/login_view_model.dart';
import 'package:travel_hub/view_models/register_view_model.dart';

void main() {
  testWidgets('App starts at login view', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => LoginViewModel()),
          ChangeNotifierProvider(create: (_) => RegisterViewModel()),
        ],
        child: const MyApp(),
      ),
    );

    // Verify that we are on the login screen (checks for a common element)
    expect(find.byType(ElevatedButton), findsWidgets);
  });
}
