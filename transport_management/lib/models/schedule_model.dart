import 'route_model.dart';
import 'bus_model.dart';

class Schedule {
  final int id;
  final BusRoute route;
  final Bus bus;
  final Map<String, dynamic> driver;
  final DateTime date;
  final String departureTime;
  final String arrivalTime;
  final int totalSeats;
  final int availableSeats;

  Schedule({
    required this.id,
    required this.route,
    required this.bus,
    required this.driver,
    required this.date,
    required this.departureTime,
    required this.arrivalTime,
    required this.totalSeats,
    required this.availableSeats,
  });

  factory Schedule.fromJson(Map<String, dynamic> json) {
    return Schedule(
      id: json['id'],
      route: BusRoute.fromJson(json['route']),
      bus: Bus.fromJson(json['bus']),
      driver: json['driver'],
      date: DateTime.parse(json['date']),
      departureTime: json['departure_time'],
      arrivalTime: json['arrival_time'],
      totalSeats: json['total_seats'],
      availableSeats: json['available_seats'],
    );
  }

  int get occupiedSeats => totalSeats - availableSeats;
  double get occupancyRate => (occupiedSeats / totalSeats) * 100;
  
  String get seatStatus {
    if (availableSeats > totalSeats * 0.5) {
      return 'Plenty of seats';
    } else if (availableSeats > 0) {
      return '$availableSeats seats left';
    } else {
      return 'Full';
    }
  }

  String get driverName => driver['name'] ?? 'Unknown';
}