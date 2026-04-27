import 'package:flutter/material.dart';
import 'habitacion.dart';

class Reservation {
  final String id;
  final Habitacion room;
  final DateTimeRange dateRange;
  final int guestCount;
  final DateTime createdAt;

  Reservation({
    required this.id,
    required this.room,
    required this.dateRange,
    required this.guestCount,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'room': room.toJson(),
      'dateRange': {
        'start': dateRange.start.toIso8601String(),
        'end': dateRange.end.toIso8601String(),
      },
      'guestCount': guestCount,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  factory Reservation.fromJson(Map<String, dynamic> json) {
    final dateRangeJson = json['dateRange'] as Map<String, dynamic>? ?? {};
    return Reservation(
      id: json['id'] as String? ?? '',
      room: Habitacion.fromJson(json['room'] as Map<String, dynamic>? ?? {}),
      dateRange: DateTimeRange(
        start: DateTime.parse(
          dateRangeJson['start'] as String? ?? DateTime.now().toIso8601String(),
        ),
        end: DateTime.parse(
          dateRangeJson['end'] as String? ??
              DateTime.now().add(const Duration(days: 1)).toIso8601String(),
        ),
      ),
      guestCount: json['guestCount'] as int? ?? 1,
      createdAt: DateTime.parse(
        json['createdAt'] as String? ?? DateTime.now().toIso8601String(),
      ),
    );
  }
}
