class Habitacion {
  final String imageUrl;
  final String title;
  final String location;
  final List<String> amenities;
  final bool isSpecialOffer;

  Habitacion({
    required this.imageUrl,
    required this.title,
    required this.location,
    required this.amenities,
    this.isSpecialOffer = false,
  });

  factory Habitacion.fromJson(Map<String, dynamic> json) {
    return Habitacion(
      imageUrl: json['imageUrl'] as String? ?? '',
      title: json['title'] as String? ?? '',
      location: json['location'] as String? ?? '',
      amenities: List<String>.from(json['amenities'] ?? []),
      isSpecialOffer: json['isSpecialOffer'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'imageUrl': imageUrl,
      'title': title,
      'location': location,
      'amenities': amenities,
      'isSpecialOffer': isSpecialOffer,
    };
  }
}
