class Habitacion {
  final String imageUrl;
  final String title;
  final String location;
  final List<String> amenities;
  final bool isSpecialOffer;
  final double price;

  Habitacion({
    required this.imageUrl,
    required this.title,
    required this.location,
    required this.amenities,
    required this.price,
    this.isSpecialOffer = false,
  });

  factory Habitacion.fromJson(Map<String, dynamic> json) {
    return Habitacion(
      imageUrl: json['imageUrl'] as String? ?? '',
      title: json['title'] as String? ?? '',
      location: json['location'] as String? ?? '',
      amenities: List<String>.from(json['amenities'] ?? []),
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      isSpecialOffer: json['isSpecialOffer'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'imageUrl': imageUrl,
      'title': title,
      'location': location,
      'amenities': amenities,
      'price': price,
      'isSpecialOffer': isSpecialOffer,
    };
  }
}
