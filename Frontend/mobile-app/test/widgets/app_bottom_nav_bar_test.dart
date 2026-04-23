import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/view_models/search_view_model.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';
import 'package:travel_hub/widgets/app_bottom_nav_bar.dart';

Widget _buildTestApp({
  required Widget child,
  NavigatorObserver? navigatorObserver,
}) {
  return MultiProvider(
    providers: [
      ChangeNotifierProvider(create: (_) => SearchViewModel()),
      ChangeNotifierProvider(create: (_) => UserPreferencesViewModel()),
    ],
    child: MaterialApp(
      locale: const Locale('en'),
      navigatorObservers: navigatorObserver == null ? const [] : [navigatorObserver],
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('es')],
      home: Scaffold(body: child),
    ),
  );
}

void main() {
  testWidgets('renders localized labels and uses currentIndex', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      _buildTestApp(
        child: const AppBottomNavBar(currentIndex: 1),
      ),
    );

    expect(find.text('Search'), findsOneWidget);
    expect(find.text('Bookings'), findsOneWidget);
    expect(find.text('Profile'), findsOneWidget);

    final bottomNavigationBar = tester.widget<BottomNavigationBar>(
      find.byType(BottomNavigationBar),
    );
    expect(bottomNavigationBar.currentIndex, 1);
  });

  testWidgets('calls onTap when a callback is provided', (
    WidgetTester tester,
  ) async {
    int? tappedIndex;

    await tester.pumpWidget(
      _buildTestApp(
        child: AppBottomNavBar(
          currentIndex: 0,
          onTap: (index) => tappedIndex = index,
        ),
      ),
    );

    await tester.tap(find.text('Profile'));
    await tester.pump();

    expect(tappedIndex, 2);
  });

  testWidgets('pushes MainNavigationView when no callback is provided', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      _buildTestApp(
        child: const AppBottomNavBar(currentIndex: 0),
      ),
    );

    await tester.tap(find.text('Bookings'));
    await tester.pumpAndSettle();

    expect(find.text('Bookings'), findsWidgets);
    final bottomNavigationBar = tester.widget<BottomNavigationBar>(
      find.byType(BottomNavigationBar),
    );
    expect(bottomNavigationBar.currentIndex, 1);
  });
}