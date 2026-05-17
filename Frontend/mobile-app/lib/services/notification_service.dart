import 'dart:async';
import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

import '../models/notification.dart';
import 'user_service.dart';

class NotificationService {
  static final StreamController<String> onNotificationTap =
      StreamController<String>.broadcast();

  final String _baseUrl =
      dotenv.env['NOTIFICATION_API_BASE_URL'] ?? 'http://10.0.2.2/notification';
  final UserService _userService = UserService();

  static Future<void> registerDeviceToken(String token) async {
    try {
      final userService = UserService();
      final userId = await userService.getUserId();

      final baseUrl =
          dotenv.env['NOTIFICATION_API_BASE_URL'] ??
          'http://10.0.2.2/notification';
      final response = await http.post(
        Uri.parse('$baseUrl/notificaciones/device-token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_id': userId, 'token': token}),
      );
      if (response.statusCode != 200) {
        print('Error registering device token: ${response.body}');
      }
    } catch (e) {
      print('Exception registering device token: $e');
    }
  }

  Future<List<NotificationModel>> fetchNotifications() async {
    final userId = await _userService.getUserId();

    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/notificaciones?userId=$userId'),
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => NotificationModel.fromJson(json)).toList();
      }
    } catch (e) {
      print('Error fetching notifications: $e');
    }
    return [];
  }

  Future<void> markAsRead(String id) async {
    try {
      await http.patch(Uri.parse('$_baseUrl/notificaciones/$id/leida'));
    } catch (e) {
      print('Error marking notification as read: $e');
    }
  }
}
