class Resena {
  final String userName;
  final double rating;
  final String comment;
  final String date;
  final String? userImageUrl;

  Resena({
    required this.userName,
    required this.rating,
    required this.comment,
    required this.date,
    this.userImageUrl,
  });

  factory Resena.fromJson(Map<String, dynamic> json) {
    return Resena(
      userName: json['userName'] as String? ?? '',
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
      comment: json['comment'] as String? ?? '',
      date: json['date'] as String? ?? '',
      userImageUrl: json['userImageUrl'] as String?,
    );
  }
}
