class Destination {
  final String imageUrl;
  final String title;
  final String location;
  final double rating;
  final String price;

  Destination({
    required this.imageUrl,
    required this.title,
    required this.location,
    required this.rating,
    required this.price,
  });

  factory Destination.fromJson(Map<String, dynamic> json) {
    return Destination(
      imageUrl: json['imageUrl'] as String? ?? '',
      title: json['title'] as String? ?? '',
      location: json['location'] as String? ?? '',
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      price: json['price'] as String? ?? '0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'imageUrl': imageUrl,
      'title': title,
      'location': location,
      'rating': rating,
      'price': price,
    };
  }
}
