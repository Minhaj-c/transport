import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  User? _user;
  bool _isLoading = true;

  User? get user => _user;
  bool get isLoggedIn => _user != null;
  bool get isLoading => _isLoading;
  bool get isPassenger => _user?.isPassenger ?? false;
  bool get isDriver => _user?.isDriver ?? false;

  AuthProvider() {
    _loadUser();
  }

  Future<void> _loadUser() async {
    _isLoading = true;
    notifyListeners();

    _user = await AuthService.getStoredUser();

    _isLoading = false;
    notifyListeners();
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final result = await AuthService.login(
      email: email,
      password: password,
    );

    if (result['success']) {
      _user = result['user'];
      notifyListeners();
    }

    return result;
  }

  Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String role,
  }) async {
    final result = await AuthService.signup(
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
      role: role,
    );

    return result;
  }

  Future<void> logout() async {
    await AuthService.logout();
    _user = null;
    notifyListeners();
  }
}