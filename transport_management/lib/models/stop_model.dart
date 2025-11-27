class Stop {
  final int id;
  final String name;
  final int sequence;
  final double distanceFromOrigin;
  final bool isLimitedStop;

  Stop({
    required this.id,
    required this.name,
    required this.sequence,
    required this.distanceFromOrigin,
    required this.isLimitedStop,
  });

  factory Stop.fromJson(Map<String, dynamic> json) {
    return Stop(
      id: json['id'],
      name: json['name'],
      sequence: json['sequence'],
      distanceFromOrigin: double.parse(json['distance_from_origin'].toString()),
      isLimitedStop: json['is_limited_stop'] ?? false,
    );
  }

  String get distanceInfo => '${distanceFromOrigin.toStringAsFixed(1)} km';
}