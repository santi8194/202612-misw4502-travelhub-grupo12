import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/l10n/app_localizations.dart';
import 'package:travel_hub/view_models/register_view_model.dart';
import 'package:travel_hub/views/register_view.dart';
import 'package:travel_hub/widgets/custom_text_field.dart';

class MockRegisterViewModel extends Mock implements RegisterViewModel {}

void main() {
  testWidgets('RegisterView form interaction', (WidgetTester tester) async {
    final mockVM = MockRegisterViewModel();
    final formKey = GlobalKey<FormState>();

    when(() => mockVM.formKey).thenReturn(formKey);
    when(() => mockVM.isLoading).thenReturn(false);
    when(() => mockVM.fullName).thenReturn('');
    when(() => mockVM.email).thenReturn('');
    when(() => mockVM.password).thenReturn('');
    when(() => mockVM.confirmPassword).thenReturn('');

    await tester.pumpWidget(
      ChangeNotifierProvider<RegisterViewModel>.value(
        value: mockVM,
        child: MaterialApp(
          routes: {'/home': (context) => const Scaffold(body: Text('Home'))},
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: [Locale('en'), Locale('es')],
          home: RegisterView(),
        ),
      ),
    );

    // Enter details
    await tester.enterText(find.byType(CustomTextField).at(0), 'John Doe');
    verify(() => mockVM.setFullName('John Doe')).called(1);

    await tester.enterText(
      find.byType(CustomTextField).at(1),
      'john@example.com',
    );
    verify(() => mockVM.setEmail('john@example.com')).called(1);

    await tester.enterText(find.byType(CustomTextField).at(2), 'password123');
    verify(() => mockVM.setPassword('password123')).called(1);

    await tester.enterText(find.byType(CustomTextField).at(3), 'password123');
    verify(() => mockVM.setConfirmPassword('password123')).called(1);

    // Submit
    when(() => mockVM.register()).thenAnswer((_) async => true);
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    verify(() => mockVM.register()).called(1);
  });
}
