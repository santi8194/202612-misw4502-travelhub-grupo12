import 'package:shared_preferences/shared_preferences.dart';

class UserService {
  static const String _userIdKey = 'userId';

  Future<String> getUserId() async {
    return 'cc912e74-927e-4166-802b-3ba6a3615ebf'; // Hardcoded for testing
    final prefs = await SharedPreferences.getInstance();
    String? userId = prefs.getString(_userIdKey);

    if (userId == null) {
      userId = 'user_${DateTime.now().millisecondsSinceEpoch}';
      await prefs.setString(_userIdKey, userId);
      print('Generated new test userId: $userId');
    }

    return userId;
  }
}
