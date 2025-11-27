import 'stop_model.dart';

class BusRoute {
  final int id;
  final String number;
  final String name;
  final String? description;
  final String origin;
  final String destination;
  final double totalDistance;
  final double duration;
  final List<Stop> stops;

  BusRoute({
    required this.id,
    required this.number,
    required this.name,
    this.description,
    required this.origin,
    required this.destination,
    required this.totalDistance,
    required this.duration,
    this.stops = const [],
  });

  factory BusRoute.fromJson(Map<String, dynamic> json) {
    return BusRoute(
      id: json['id'],
      number: json['number'],
      name: json['name'],
      description: json['description'],
      origin: json['origin'],
      destination: json['destination'],
      totalDistance: double.parse(json['total_distance'].toString()),
      duration: double.parse(json['duration'].toString()),
      stops: json['stops'] != null
          ? (json['stops'] as List).map((s) => Stop.fromJson(s)).toList()
          : [],
    );
  }

  String get routeInfo => '$origin → $destination';
  String get distanceInfo => '${totalDistance.toStringAsFixed(1)} km';
  String get durationInfo {
    final hours = duration.floor();
    final minutes = ((duration - hours) * 60).round();
    if (hours > 0) {
      return '${hours}h ${minutes}m';
    }
    return '${minutes}m';
  }
}