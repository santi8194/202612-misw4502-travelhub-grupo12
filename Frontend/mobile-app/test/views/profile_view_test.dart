import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';
import 'package:travel_hub/views/profile_view.dart';

class MockUserPreferencesViewModel extends Mock
    implements UserPreferencesViewModel {}

void main() {
  late MockUserPreferencesViewModel mockUserVM;

  setUp(() {
    mockUserVM = MockUserPreferencesViewModel();
    when(() => mockUserVM.country).thenReturn('Colombia');
    when(() => mockUserVM.setCountry(any())).thenAnswer((_) async => {});
  });

  Widget createWidgetUnderTest() {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<UserPreferencesViewModel>.value(
          value: mockUserVM,
        ),
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
        home: ProfileView(),
      ),
    );
  }

  testWidgets('ProfileView renders correctly', (tester) async {
    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    expect(find.text('Perfil'), findsOneWidget);
    expect(find.text('País'), findsOneWidget);
    expect(find.text('Colombia'), findsOneWidget);
  });

  testWidgets('ProfileView updates country via dropdown', (tester) async {
    await tester.pumpWidget(createWidgetUnderTest());
    await tester.pump();

    // Open dropdown
    await tester.tap(find.byType(DropdownButtonFormField<String>));
    await tester.pumpAndSettle();

    // Select Argentina
    await tester.tap(find.text('Argentina').last);
    await tester.pumpAndSettle();

    verify(() => mockUserVM.setCountry('Argentina')).called(1);
  });
}
