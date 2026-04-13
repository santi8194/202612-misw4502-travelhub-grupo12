import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

/// Monitors network connectivity and notifies listeners of changes.
///
/// Exposes [isOnline] for synchronous checks and a [onConnectivityChanged]
/// stream so other services can react when the device goes online/offline.
class ConnectivityService extends ChangeNotifier {
  final Connectivity? _connectivity;
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  bool _isOnline = true;

  bool get isOnline => _isOnline;

  /// Stream controller that emits `true` when going online, `false` when going offline.
  final StreamController<bool> _connectivityStreamController =
      StreamController<bool>.broadcast();

  Stream<bool> get onConnectivityChanged => _connectivityStreamController.stream;

  ConnectivityService({Connectivity? connectivity})
      : _connectivity = connectivity ?? Connectivity() {
    _init();
  }

  /// Test-only constructor that skips platform channel initialization.
  @visibleForTesting
  ConnectivityService.test({bool online = true})
      : _connectivity = null,
        _isOnline = online;

  Future<void> _init() async {
    if (_connectivity == null) return;
    // Check initial state
    final results = await _connectivity.checkConnectivity();
    _updateStatus(results);

    // Listen for changes
    _subscription = _connectivity.onConnectivityChanged.listen(_updateStatus);
  }

  void _updateStatus(List<ConnectivityResult> results) {
    final wasOnline = _isOnline;
    _isOnline = results.any((r) => r != ConnectivityResult.none);

    if (wasOnline != _isOnline) {
      _connectivityStreamController.add(_isOnline);
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _connectivityStreamController.close();
    super.dispose();
  }
}
