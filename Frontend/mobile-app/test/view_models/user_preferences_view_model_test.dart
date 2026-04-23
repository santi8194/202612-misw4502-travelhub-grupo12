import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';

void main() {
  test('starts without a selected country', () {
    final viewModel = UserPreferencesViewModel();

    expect(viewModel.country, isNull);
  });

  test('setCountry updates the value and notifies listeners once', () {
    final viewModel = UserPreferencesViewModel();
    var notifications = 0;

    viewModel.addListener(() {
      notifications += 1;
    });

    viewModel.setCountry('Colombia');

    expect(viewModel.country, 'Colombia');
    expect(notifications, 1);
  });

  test('setCountry does not notify when the value is unchanged', () {
    final viewModel = UserPreferencesViewModel();
    var notifications = 0;

    viewModel.addListener(() {
      notifications += 1;
    });

    viewModel.setCountry('Colombia');
    viewModel.setCountry('Colombia');

    expect(notifications, 1);
  });
}
