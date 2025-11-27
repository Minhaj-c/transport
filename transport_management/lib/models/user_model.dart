class User {
  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String role;
  final DateTime? dateJoined;

  User({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.role,
    this.dateJoined,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      role: json['role'],
      dateJoined: json['date_joined'] != null 
          ? DateTime.parse(json['date_joined'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'role': role,
    };
  }

  String get fullName {
    final name = '${firstName} ${lastName}'.trim();
    return name.isEmpty ? email : name;
  }

  bool get isPassenger => role == 'passenger';
  bool get isDriver => role == 'driver';
  bool get isAdmin => role == 'admin';
}