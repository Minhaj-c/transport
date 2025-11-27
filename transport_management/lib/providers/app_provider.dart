import 'package:flutter/material.dart';
import '../models/route_model.dart';
import '../models/schedule_model.dart';
import '../services/api_service.dart';

class AppProvider with ChangeNotifier {
  List<BusRoute> _routes = [];
  List<Schedule> _schedules = [];
  bool _isLoadingRoutes = false;
  bool _isLoadingSchedules = false;

  List<BusRoute> get routes => _routes;
  List<Schedule> get schedules => _schedules;
  bool get isLoadingRoutes => _isLoadingRoutes;
  bool get isLoadingSchedules => _isLoadingSchedules;

  // Load all routes
  Future<void> loadRoutes() async {
    _isLoadingRoutes = true;
    notifyListeners();

    try {
      _routes = await ApiService.getRoutes();
    } catch (e) {
      print('Error loading routes: $e');
    }

    _isLoadingRoutes = false;
    notifyListeners();
  }

  // Load schedules
  Future<void> loadSchedules({int? routeId, String? date}) async {
    _isLoadingSchedules = true;
    notifyListeners();

    try {
      _schedules = await ApiService.getSchedules(
        routeId: routeId,
        date: date,
      );
    } catch (e) {
      print('Error loading schedules: $e');
    }

    _isLoadingSchedules = false;
    notifyListeners();
  }

  // Get route by ID
  BusRoute? getRouteById(int id) {
    try {
      return _routes.firstWhere((route) => route.id == id);
    } catch (e) {
      return null;
    }
  }
}