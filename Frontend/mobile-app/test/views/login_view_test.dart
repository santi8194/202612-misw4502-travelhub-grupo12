import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/views/login_view.dart';
import 'package:travel_hub/view_models/login_view_model.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:travel_hub/l10n/app_localizations.dart';

void main() {
  testWidgets('LoginView renders and allows typing', (WidgetTester tester) async {
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => LoginViewModel(),
        child: MaterialApp(

          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: [Locale('en'), Locale('es')],
          home: LoginView(),
          routes: {'/home': (context) => const Scaffold(body: Text('Home'))},
        ),
      ),

    );

    expect(find.text('Email address'), findsOneWidget);

    expect(find.text('Password'), findsOneWidget);

    await tester.enterText(find.byType(TextFormField).first, 'test@example.com');
    await tester.enterText(find.byType(TextFormField).at(1), 'password');
    
    await tester.tap(find.byType(ElevatedButton));

    await tester.pump();
    
    // Should show loading
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    // Wait for the mock 2-second delay to finish, otherwise the test fails with "pending timers"
    await tester.pumpAndSettle(const Duration(seconds: 2));
  });
}
