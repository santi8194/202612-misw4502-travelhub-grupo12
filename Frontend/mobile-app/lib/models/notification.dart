class NotificationModel {
  final String id;
  final String tipo;
  final String titulo;
  final String cuerpo;
  final String? reservaId;
  final DateTime timestamp;
  final bool leida;

  NotificationModel({
    required this.id,
    required this.tipo,
    required this.titulo,
    required this.cuerpo,
    this.reservaId,
    required this.timestamp,
    required this.leida,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] ?? '',
      tipo: json['tipo'] ?? '',
      titulo: json['titulo'] ?? '',
      cuerpo: json['cuerpo'] ?? '',
      reservaId: json['reserva_id'],
      timestamp: DateTime.parse(json['timestamp']).toLocal(),
      leida: json['leida'] ?? false,
    );
  }
}
