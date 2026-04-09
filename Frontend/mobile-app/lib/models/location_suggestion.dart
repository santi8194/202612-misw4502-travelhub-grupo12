class LocationSuggestion {
  final String ciudad;
  final String estadoProvincia;
  final String pais;

  const LocationSuggestion({
    required this.ciudad,
    required this.estadoProvincia,
    required this.pais,
  });

  factory LocationSuggestion.fromJson(Map<String, dynamic> json) {
    return LocationSuggestion(
      ciudad: json['ciudad'] as String,
      estadoProvincia: json['estado_provincia'] as String,
      pais: json['pais'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'ciudad': ciudad,
      'estado_provincia': estadoProvincia,
      'pais': pais,
    };
  }

  String get displayName => '$ciudad, $estadoProvincia, $pais';

  @override
  String toString() => displayName;
}
