import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/view_models/login_view_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('LoginViewModel Tests', () {
    late LoginViewModel viewModel;

    setUp(() {
      viewModel = LoginViewModel();
    });

    test('Initial state is correct', () {
      expect(viewModel.email, '');
      expect(viewModel.password, '');
      expect(viewModel.isLoading, false);
    });

    test('setEmail updates value', () {
      viewModel.setEmail('test@example.com');
      expect(viewModel.email, 'test@example.com');
    });

    test('setPassword updates value', () {
      viewModel.setPassword('secret');
      expect(viewModel.password, 'secret');
    });

    test('login returns false when validation fails', () async {
      // formKey.currentState is null in unit tests unless we pump a widget
      final result = await viewModel.login();
      expect(result, false);
    });
  });
}
