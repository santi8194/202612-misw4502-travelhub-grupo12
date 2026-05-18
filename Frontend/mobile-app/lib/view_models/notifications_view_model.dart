import 'package:flutter/material.dart';
import 'package:flutter_app_badger/flutter_app_badger.dart';

import '../models/notification.dart';
import '../services/notification_service.dart';

class NotificationsViewModel extends ChangeNotifier {
  final NotificationService _service = NotificationService();
  List<NotificationModel> notifications = [];
  bool isLoading = true;

  NotificationsViewModel() {
    fetchNotifications();
  }

  Future<void> fetchNotifications() async {
    isLoading = true;
    notifyListeners();
    notifications = await _service.fetchNotifications();
    _updateAppBadge();
    isLoading = false;
    notifyListeners();
  }

  void _updateAppBadge() {
    final count = unreadCount;
    if (count > 0) {
      FlutterAppBadger.updateBadgeCount(count);
    } else {
      FlutterAppBadger.removeBadge();
    }
  }

  int get unreadCount {
    return notifications.where((n) => !n.leida).length;
  }

  Future<void> markAsRead(String id) async {
    final index = notifications.indexWhere((n) => n.id == id);
    if (index != -1 && !notifications[index].leida) {
      notifications[index] = NotificationModel(
        id: notifications[index].id,
        tipo: notifications[index].tipo,
        titulo: notifications[index].titulo,
        cuerpo: notifications[index].cuerpo,
        reservaId: notifications[index].reservaId,
        timestamp: notifications[index].timestamp,
        leida: true,
      );
      _updateAppBadge();
      notifyListeners();
      await _service.markAsRead(id);
    }
  }

  void onNotificationTap(NotificationModel notification) {
    if (!notification.leida) {
      markAsRead(notification.id);
    }
    if (notification.reservaId != null) {
      NotificationService.onNotificationTap.add(notification.reservaId!);
    }
  }
}
