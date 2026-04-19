import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../models/habitacion.dart';
import '../view_models/confirm_reservation_view_model.dart';

class ConfirmReservationView extends StatelessWidget {
  final Habitacion room;
  final DateTimeRange dateRange;
  final int guests;

  const ConfirmReservationView({
    super.key,
    required this.room,
    required this.dateRange,
    required this.guests,
  });

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ConfirmReservationViewModel(
        room: room,
        selectedDateRange: dateRange,
        guests: guests,
      ),
      child: Consumer<ConfirmReservationViewModel>(
        builder: (context, viewModel, child) {
          final l10n = AppLocalizations.of(context)!;

          final nights = dateRange.duration.inDays;
          final pricePerNight = room.price;
          final subtotal = nights * pricePerNight;
          final taxes = subtotal * 0.19;
          final total = subtotal + taxes;

          final start = dateRange.start;
          final end = dateRange.end;

          final formattedDates =
              "${start.day} - ${end.day} Mar"; // puedes mejorar formato

          return Scaffold(
            backgroundColor: const Color(0xFFF7F7F7),
            appBar: AppBar(
              backgroundColor: Colors.white,
              elevation: 0,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, color: Colors.black),
                onPressed: () => Navigator.pop(context),
              ),
              title: const Text(
                "Confirmar Reserva",
                style: TextStyle(
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                ),
              ),
              centerTitle: true,
            ),

            /// 🔻 BOTÓN FIJO ABAJO
            bottomNavigationBar: Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(
                height: 60,
                child: ElevatedButton(
                  onPressed: viewModel.isConfirming
                      ? null
                      : () async {
                          final confirmed = await viewModel
                              .confirmReservation();
                          if (confirmed && context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text("Reserva confirmada"),
                              ),
                            );
                          }
                        },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2F4B8C),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: viewModel.isConfirming
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                          "Confirmar y Pagar",
                          style: TextStyle(fontSize: 16),
                        ),
                ),
              ),
            ),

            body: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _buildHotelCard(),
                  const SizedBox(height: 16),
                  _buildTripDetails(formattedDates, "$guests Adultos"),
                  const SizedBox(height: 16),
                  _buildPriceBreakdown(
                    nights,
                    pricePerNight,
                    subtotal,
                    taxes,
                    total,
                  ),
                  const SizedBox(height: 16),
                  _buildPaymentMethod(),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  /// 🏨 HOTEL CARD
  Widget _buildHotelCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardStyle(),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: Image.network(
              room.imageUrl,
              width: 70,
              height: 70,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  width: 70,
                  height: 70,
                  color: Colors.grey.shade200,
                  alignment: Alignment.center,
                  child: const Icon(
                    Icons.broken_image,
                    color: Colors.grey,
                    size: 28,
                  ),
                );
              },
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  room.title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(room.location, style: const TextStyle(color: Colors.grey)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 📅 DETALLES DEL VIAJE
  Widget _buildTripDetails(String dates, String guests) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardStyle(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "DETALLES DEL VIAJE",
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _detailItem(Icons.calendar_today, "Fechas", dates),
              ),
              const SizedBox(width: 12),
              Expanded(child: _detailItem(Icons.people, "Huéspedes", guests)),
            ],
          ),
        ],
      ),
    );
  }

  /// 💰 PRECIOS
  Widget _buildPriceBreakdown(
    int nights,
    double pricePerNight,
    double subtotal,
    double taxes,
    double total,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardStyle(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "DESGLOSE DE PRECIOS",
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _priceRow(
            "$pricePerNight US\$ x $nights noches",
            "${subtotal.toStringAsFixed(0)} US\$",
          ),
          _priceRow("Impuestos y cargos", "${taxes.toStringAsFixed(0)} US\$"),
          const Divider(),
          _priceRow("Total", "${total.toStringAsFixed(0)} US\$", isBold: true),
        ],
      ),
    );
  }

  /// 💳 MÉTODO DE PAGO
  Widget _buildPaymentMethod() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardStyle(),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 30,
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(6),
            ),
          ),
          const SizedBox(width: 16),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Método de Pago",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  "Visa terminada en •••• 4242",
                  style: TextStyle(color: Colors.grey),
                ),
              ],
            ),
          ),
          const Icon(Icons.chevron_right),
        ],
      ),
    );
  }

  /// 🎨 ESTILO CARD
  BoxDecoration _cardStyle() {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: Colors.grey.shade200),
    );
  }

  /// 🔹 ITEM DETALLE
  Widget _detailItem(IconData icon, String title, String value) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Colors.grey),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(color: Colors.grey)),
            Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ],
    );
  }

  /// 🔹 FILA PRECIO
  Widget _priceRow(String title, String value, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title),
          Text(
            value,
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}
