import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/view_models/user_preferences_view_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('starts with USA when language is not Spanish', () {
    final viewModel = UserPreferencesViewModel(languageCode: 'en');

    expect(viewModel.country, 'USA');
  });

  test('starts with Colombia when language is Spanish', () {
    final viewModel = UserPreferencesViewModel(languageCode: 'es');

    expect(viewModel.country, 'Colombia');
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
