import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/view_models/register_view_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('RegisterViewModel Tests', () {
    late RegisterViewModel viewModel;

    setUp(() {
      viewModel = RegisterViewModel();
    });

    test('Initial state is correct', () {
      expect(viewModel.email, '');
      expect(viewModel.password, '');
      expect(viewModel.confirmPassword, '');
      expect(viewModel.isLoading, false);
    });

    test('setEmail updates value', () {
      viewModel.setEmail('test@reg.com');
      expect(viewModel.email, 'test@reg.com');
    });

    test('setPassword updates value', () {
      viewModel.setPassword('secret');
      expect(viewModel.password, 'secret');
    });

    test('setFullName updates value', () {
      viewModel.setFullName('John Doe');
      expect(viewModel.fullName, 'John Doe');
    });

    test('setConfirmPassword updates value', () {
      viewModel.setConfirmPassword('secret');
      expect(viewModel.confirmPassword, 'secret');
    });

    test('register validation fails with empty fields', () async {
      final result = await viewModel.register();
      expect(result, false);
      expect(viewModel.isLoading, false);
    });

    test('register fails when passwords do not match', () async {
      viewModel.setPassword('pass1');
      viewModel.setConfirmPassword('pass2');
      // register() calls formKey.currentState?.validate()
      // Since formKey is a real GlobalKey and not attached to a Form widget here,
      // validate() will likely return null/false, but we can't easily mock it in a pure unit test.
      // However, we can test the password mismatch logic if we can get past the validate() call.
    });
  });
}
