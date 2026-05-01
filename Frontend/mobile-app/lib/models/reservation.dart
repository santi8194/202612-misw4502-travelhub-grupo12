import 'package:flutter/material.dart';

import 'habitacion.dart';

class Reservation {
  final String id;
  final Habitacion room;
  final DateTimeRange dateRange;
  final int guestCount;
  final DateTime createdAt;
  final String confirmationCode;
  final String status;
  final String hotelName;
  final String hotelAddress;
  final String hotelPhone;

  Reservation({
    required this.id,
    required this.room,
    required this.dateRange,
    required this.guestCount,
    DateTime? createdAt,
    this.confirmationCode = '',
    this.status = '',
    this.hotelName = '',
    this.hotelAddress = '',
    this.hotelPhone = '',
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
      'confirmationCode': confirmationCode,
      'status': status,
      'hotelName': hotelName,
      'hotelAddress': hotelAddress,
      'hotelPhone': hotelPhone,
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
      confirmationCode: json['confirmationCode'] as String? ?? '',
      status: json['status'] as String? ?? '',
      hotelName: json['hotelName'] as String? ?? '',
      hotelAddress: json['hotelAddress'] as String? ?? '',
      hotelPhone: json['hotelPhone'] as String? ?? '',
    );
  }

  Reservation copyWith({
    String? id,
    Habitacion? room,
    DateTimeRange? dateRange,
    int? guestCount,
    DateTime? createdAt,
    String? confirmationCode,
    String? status,
    String? hotelName,
    String? hotelAddress,
    String? hotelPhone,
  }) {
    return Reservation(
      id: id ?? this.id,
      room: room ?? this.room,
      dateRange: dateRange ?? this.dateRange,
      guestCount: guestCount ?? this.guestCount,
      createdAt: createdAt ?? this.createdAt,
      confirmationCode: confirmationCode ?? this.confirmationCode,
      status: status ?? this.status,
      hotelName: hotelName ?? this.hotelName,
      hotelAddress: hotelAddress ?? this.hotelAddress,
      hotelPhone: hotelPhone ?? this.hotelPhone,
    );
  }
}
