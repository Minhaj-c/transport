class Bus {
  final int id;
  final String numberPlate;
  final int capacity;
  final double mileage;
  final String serviceType;
  final bool isActive;
  final double? currentLatitude;
  final double? currentLongitude;
  final DateTime? lastLocationUpdate;
  final bool isRunning;

  Bus({
    required this.id,
    required this.numberPlate,
    required this.capacity,
    required this.mileage,
    required this.serviceType,
    required this.isActive,
    this.currentLatitude,
    this.currentLongitude,
    this.lastLocationUpdate,
    required this.isRunning,
  });

  factory Bus.fromJson(Map<String, dynamic> json) {
    return Bus(
      id: json['id'],
      numberPlate: json['number_plate'],
      capacity: json['capacity'],
      mileage: double.parse(json['mileage'].toString()),
      serviceType: json['service_type'],
      isActive: json['is_active'] ?? true,
      currentLatitude: json['current_latitude'] != null 
          ? double.parse(json['current_latitude'].toString()) 
          : null,
      currentLongitude: json['current_longitude'] != null
          ? double.parse(json['current_longitude'].toString())
          : null,
      lastLocationUpdate: json['last_location_update'] != null
          ? DateTime.parse(json['last_location_update'])
          : null,
      isRunning: json['is_running'] ?? false,
    );
  }
}