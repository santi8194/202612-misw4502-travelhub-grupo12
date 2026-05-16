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
      expect(viewModel.fullName, '');
      expect(viewModel.confirmPassword, '');
      expect(viewModel.isLoading, false);
    });

    test('setEmail updates value', () {
      viewModel.setEmail('test@example.com');
      expect(viewModel.email, 'test@example.com');
    });

    test('setPassword updates value', () {
      viewModel.setPassword('password123');
      expect(viewModel.password, 'password123');
    });

    test('setFullName updates value', () {
      viewModel.setFullName('John Doe');
      expect(viewModel.fullName, 'John Doe');
    });

    test('setConfirmPassword updates value', () {
      viewModel.setConfirmPassword('password123');
      expect(viewModel.confirmPassword, 'password123');
    });

    test('register fails when passwords do not match', () async {
      viewModel.setPassword('pass1');
      viewModel.setConfirmPassword('pass2');
      final result = await viewModel.register();
      expect(result, false);
    });

    test('register returns false on initial empty state', () async {
      final result = await viewModel.register();
      expect(result, false);
    });
  });
}
