import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/views/register_view.dart';
import 'package:travel_hub/view_models/register_view_model.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:travel_hub/l10n/app_localizations.dart';

void main() {
  testWidgets('RegisterView renders and allows typing', (WidgetTester tester) async {
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => RegisterViewModel(),
        child: MaterialApp(

          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: [Locale('en'), Locale('es')],
          home: RegisterView(),
          routes: {'/home': (context) => const Scaffold(body: Text('Home'))},
        ),
      ),

    );

    expect(find.text('Full Name'), findsOneWidget);
    expect(find.textContaining('Password'), findsAtLeast(2)); // Pass and ConfPass

    await tester.enterText(find.byType(TextFormField).at(0), 'John Doe');
    await tester.enterText(find.byType(TextFormField).at(1), 'new@example.com');
    await tester.enterText(find.byType(TextFormField).at(2), 'password');
    await tester.enterText(find.byType(TextFormField).at(3), 'password');
    
    await tester.tap(find.byType(ElevatedButton));

    await tester.pump();
    
    // Should show loading
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    // Wait for the mock 2-second delay to finish, otherwise the test fails with "pending timers"
    await tester.pumpAndSettle(const Duration(seconds: 2));
  });
}
