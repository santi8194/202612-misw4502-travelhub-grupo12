import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/widgets/custom_text_field.dart';

void main() {
  testWidgets('CustomTextField renders and triggers onChanged', (WidgetTester tester) async {
    String? changedValue;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CustomTextField(
            labelText: 'Test Label',
            onChanged: (val) => changedValue = val,
            validator: (val) => val!.isEmpty ? 'Error' : null,
          ),
        ),
      ),
    );

    expect(find.text('Test Label'), findsOneWidget);
    
    await tester.enterText(find.byType(TextFormField), 'Hello');
    expect(changedValue, 'Hello');
    
    // Test validation
    final form = tester.widget<TextFormField>(find.byType(TextFormField));
    expect(form.validator!(''), 'Error');
    expect(form.validator!('ok'), null);
  });

  testWidgets('CustomTextField obscureText works', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CustomTextField(
            labelText: 'Pass',
            onChanged: (_) {},
            obscureText: true,
          ),
        ),
      ),
    );

    // Test if it builds.
    expect(find.byType(TextFormField), findsOneWidget);
  });
}

