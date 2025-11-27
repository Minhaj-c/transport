import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';
import '../models/user_model.dart';
import 'api_service.dart';

class AuthService {
  static const String _userKey = 'user_data';
  static const String _cookieKey = 'session_cookie';

  // Signup
  static Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String role,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.signup),
        headers: ApiConfig.headers,
        body: json.encode({
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
          'role': role,
        }),
      );

      final data = json.decode(response.body);

      if (response.statusCode == 201) {
        return {'success': true, 'user': data['user']};
      } else {
        return {'success': false, 'error': data['error'] ?? 'Signup failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    }
  }

  // Login
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.login),
        headers: ApiConfig.headers,
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      print('Login response status: ${response.statusCode}');
      print('Login response body: ${response.body}');
      print('Login response headers: ${response.headers}');

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        // Extract and save ALL cookies
        final setCookieHeader = response.headers['set-cookie'];
        print('Set-Cookie header: $setCookieHeader');
        
        if (setCookieHeader != null) {
          // Extract sessionid and csrftoken
          final cookies = _extractCookies(setCookieHeader);
          print('Extracted cookies: $cookies');
          
          if (cookies.isNotEmpty) {
            await _saveCookie(cookies);
            ApiService.setSessionCookie(cookies);
          }
        }

        // Save user data
        final user = User.fromJson(data['user']);
        await _saveUser(user);

        return {'success': true, 'user': user};
      } else {
        return {'success': false, 'error': data['error'] ?? 'Login failed'};
      }
    } catch (e) {
      print('Login error: $e');
      return {'success': false, 'error': 'Connection error: $e'};
    }
  }

  // Extract cookies from Set-Cookie header
  static String _extractCookies(String setCookieHeader) {
    final cookies = <String>[];
    
    // Split multiple Set-Cookie headers
    final cookieParts = setCookieHeader.split(',');
    
    for (var part in cookieParts) {
      // Extract just the cookie name=value, ignore attributes
      final cookieValue = part.split(';')[0].trim();
      
      // Only add if it's a valid cookie
      if (cookieValue.contains('=')) {
        // Check if it's sessionid or csrftoken
        if (cookieValue.startsWith('sessionid=') || 
            cookieValue.startsWith('csrftoken=')) {
          cookies.add(cookieValue);
        }
      }
    }
    
    return cookies.join('; ');
  }

  // Logout
  static Future<void> logout() async {
    try {
      final cookie = await _getCookie();
      
      await http.post(
        Uri.parse(ApiConfig.logout),
        headers: {
          ...ApiConfig.headers,
          if (cookie != null) 'Cookie': cookie,
        },
      );
    } catch (e) {
      print('Logout error: $e');
    }

    // Clear local data
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    await prefs.remove(_cookieKey);
    ApiService.setSessionCookie(null);
  }

  // Get stored user
  static Future<User?> getStoredUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userData = prefs.getString(_userKey);
    final cookie = prefs.getString(_cookieKey);

    print('Getting stored user...');
    print('User data exists: ${userData != null}');
    print('Cookie exists: ${cookie != null}');

    if (userData != null && cookie != null) {
      ApiService.setSessionCookie(cookie);
      return User.fromJson(json.decode(userData));
    }
    return null;
  }

  // Save user locally
  static Future<void> _saveUser(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, json.encode(user.toJson()));
    print('User saved to SharedPreferences');
  }

  // Save cookie
  static Future<void> _saveCookie(String cookie) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_cookieKey, cookie);
    print('Cookie saved: $cookie');
  }

  // Get cookie
  static Future<String?> _getCookie() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_cookieKey);
  }

  // Check if logged in
  static Future<bool> isLoggedIn() async {
    final user = await getStoredUser();
    return user != null;
  }
}