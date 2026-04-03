import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:travel_hub/views/busqueda_view.dart';
import 'package:travel_hub/view_models/search_view_model.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:travel_hub/l10n/app_localizations.dart';

import 'package:travel_hub/services/search_service.dart';
import 'package:travel_hub/models/hotel.dart';
import 'package:travel_hub/models/location_suggestion.dart';

class MockSearchService extends SearchService {
  @override
  Future<List<Hotel>> searchHotels({
    required query,
    required startDate,
    required endDate,
    required guests,
  }) async => [];

  @override
  Future<List<LocationSuggestion>> getLocationSuggestions(String query) async {
    return [const LocationSuggestion(ciudad: 'Bogotá', estadoProvincia: 'Bogotá D.C.', pais: 'Colombia')];
  }
}

void main() {
  testWidgets('BusquedaView UI acts on tap and triggers validations', (WidgetTester tester) async {
    final viewModel = SearchViewModel(searchService: MockSearchService());

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider<SearchViewModel>.value(value: viewModel),
        ],
        child: MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: const [
            Locale('es', ''),
            Locale('en', ''),
          ],
          home: const BusquedaView(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Tap search button without destination
    final searchButton = find.byType(ElevatedButton).first;
    await tester.tap(searchButton);
    await tester.pumpAndSettle();

    // Verify error state is activated when it's empty
    expect(viewModel.isDestinationError, true);

    // Enter a valid destination in the Autocomplete TextField
    await tester.enterText(find.byType(TextField).first, 'Bogotá, Colombia');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    FocusManager.instance.primaryFocus?.unfocus();
    await tester.pumpAndSettle();

    expect(viewModel.destinationQuery, 'Bogotá, Bogotá D.C., Colombia');
    expect(viewModel.isDestinationError, false);

    // Ensure the person icon is visible by scrolling if necessary
    final personIcon = find.byIcon(Icons.person_outline).first;
    await tester.ensureVisible(personIcon);
    await tester.pumpAndSettle();

    // Open guest bottom sheet
    await tester.tap(personIcon);
    await tester.pumpAndSettle();

    final addButton = find.byIcon(Icons.add_circle_outline).first;
    await tester.tap(addButton);
    await tester.pumpAndSettle();

    // Close the bottom sheet to update the view model
    final confirmButton = find.text('Confirmar').first;
    await tester.tap(confirmButton);
    await tester.pumpAndSettle();

    expect(viewModel.guestCount, 3);

    // Unmount to clean up
    await tester.pumpWidget(Container());
  });
}
