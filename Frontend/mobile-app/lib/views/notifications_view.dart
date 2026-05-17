import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../view_models/notifications_view_model.dart';
import '../widgets/notification_card.dart';

class NotificationsView extends StatelessWidget {
  const NotificationsView({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<NotificationsViewModel>(
      builder: (context, viewModel, child) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('Notificaciones'),
            leading: IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: () => Navigator.of(context).pop(),
            ),
          ),
          body: viewModel.isLoading
              ? const Center(child: CircularProgressIndicator())
              : viewModel.notifications.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.notifications_off,
                        size: 64,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'No tienes notificaciones',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: () => viewModel.fetchNotifications(),
                  child: ListView.builder(
                    itemCount: viewModel.notifications.length,
                    itemBuilder: (context, index) {
                      final notification = viewModel.notifications[index];
                      return NotificationCard(
                        notification: notification,
                        onTap: () {
                          viewModel.onNotificationTap(notification);
                        },
                      );
                    },
                  ),
                ),
        );
      },
    );
  }
}
