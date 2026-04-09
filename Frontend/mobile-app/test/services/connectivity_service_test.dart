import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:travel_hub/services/connectivity_service.dart';

class MockConnectivity extends Mock implements Connectivity {}

void main() {
  test('ConnectivityService initializes and monitors changes', () async {
    final mockConnectivity = MockConnectivity();

    // Initial state: online
    when(
      () => mockConnectivity.checkConnectivity(),
    ).thenAnswer((_) async => [ConnectivityResult.wifi]);
    when(() => mockConnectivity.onConnectivityChanged).thenAnswer(
      (_) => Stream.fromIterable([
        [ConnectivityResult.none], // switch to offline
        [ConnectivityResult.mobile], // switch back to online
      ]),
    );

    // Stream should have added values - listen before service creation to capture all changes
    final changes = <bool>[];
    final service = ConnectivityService(connectivity: mockConnectivity);
    service.onConnectivityChanged.listen((online) => changes.add(online));

    // We need to wait for the microtask initialization in _init()
    await Future.delayed(const Duration(milliseconds: 50));

    // Verify initial check was called
    verify(() => mockConnectivity.checkConnectivity()).called(1);

    // Wait for stream to emit all values from the mock stream
    await Future.delayed(const Duration(milliseconds: 100));

    expect(service.isOnline, true); // Last emitted was mobile
    expect(changes, isNotEmpty);

    service.dispose();
  });
}
