import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/notification.dart';

class NotificationCard extends StatelessWidget {
  final NotificationModel notification;
  final VoidCallback onTap;

  const NotificationCard({
    super.key,
    required this.notification,
    required this.onTap,
  });

  String _getRelativeTime(DateTime timestamp) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final notificationDate = DateTime(
      timestamp.year,
      timestamp.month,
      timestamp.day,
    );

    if (notificationDate == today) {
      return 'Hoy, ${DateFormat('HH:mm').format(timestamp)}';
    } else if (notificationDate == yesterday) {
      return 'Ayer, ${DateFormat('HH:mm').format(timestamp)}';
    } else {
      return DateFormat('dd MMM, HH:mm').format(timestamp);
    }
  }

  IconData _getIconForType() {
    switch (notification.tipo) {
      case 'confirmed':
        return Icons.check_circle;
      case 'discount':
        return Icons.local_offer;
      case 'checkin_reminder':
        return Icons.calendar_today;
      case 'profile_update':
        return Icons.info;
      default:
        return Icons.notifications;
    }
  }

  Color _getColorForType() {
    switch (notification.tipo) {
      case 'confirmed':
        return Colors.green;
      case 'discount':
        return Colors.orange;
      case 'checkin_reminder':
        return Colors.grey;
      case 'profile_update':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          color: notification.leida ? Colors.white : Colors.blue.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: notification.leida
                ? Colors.grey.shade200
                : Colors.blue.shade200,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: _getColorForType().withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getIconForType(),
                color: _getColorForType(),
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    notification.titulo,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    notification.cuerpo,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(color: Colors.grey.shade700, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _getRelativeTime(notification.timestamp),
                    style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                  ),
                ],
              ),
            ),
            if (!notification.leida)
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
