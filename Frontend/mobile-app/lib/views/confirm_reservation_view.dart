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

          final currencyCode = _currencyCodeForLocale(context, l10n);
          final currencyTag = l10n.currencyBubbleLabel(currencyCode);

          final screenWidth = MediaQuery.of(context).size.width;
          final scale = screenWidth / 390;
          final cardPadding = (15 * scale).clamp(14.0, 22.0);
          final imageSize = (82 * scale).clamp(72.0, 90.0);
          final titleFontSize = (18 * scale).clamp(16.0, 20.0);
          final subtitleFontSize = (15 * scale).clamp(13.0, 17.0);
          final sectionTitleSize = (16 * scale).clamp(14.0, 18.0);
          final detailLabelSize = (14 * scale).clamp(12.0, 16.0);
          final detailValueSize = (15 * scale).clamp(13.0, 17.0);
          final priceFontSize = (15 * scale).clamp(13.0, 17.0);
          final buttonFontSize = (18 * scale).clamp(16.0, 20.0);
          final buttonHeight = (64 * scale).clamp(56.0, 72.0);
          final iconSize = (16 * scale).clamp(16.0, 22.0);
          final spacing = (18 * scale).clamp(14.0, 22.0);
          final cardRadius = (20 * scale).clamp(18.0, 24.0);

          return Scaffold(
            backgroundColor: Colors.white,
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
                  fontSize: 20,
                ),
              ),
              centerTitle: true,
            ),

            bottomNavigationBar: Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              child: SizedBox(
                height: buttonHeight,
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
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                  child: viewModel.isConfirming
                      ? const CircularProgressIndicator(color: Colors.white)
                      : Text(
                          "Confirmar y Pagar",
                          style: TextStyle(
                            fontSize: buttonFontSize,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),
            ),

            body: Container(
              color: Colors.white,
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 20,
                ),
                child: Column(
                  children: [
                    _buildHotelCard(
                      imageSize: imageSize,
                      cardPadding: cardPadding,
                      spacing: spacing,
                      titleFontSize: titleFontSize,
                      subtitleFontSize: subtitleFontSize,
                      radius: cardRadius,
                    ),
                    SizedBox(height: spacing),
                    _buildTripDetails(
                      formattedDates,
                      "$guests Adultos",
                      cardPadding: cardPadding,
                      sectionTitleSize: sectionTitleSize,
                      spacing: spacing,
                      iconSize: iconSize,
                      labelSize: detailLabelSize,
                      valueSize: detailValueSize,
                      radius: cardRadius,
                    ),
                    SizedBox(height: spacing),
                    _buildPriceBreakdown(
                      nights,
                      pricePerNight,
                      subtotal,
                      taxes,
                      total,
                      currencyTag: currencyTag,
                      cardPadding: cardPadding,
                      sectionTitleSize: sectionTitleSize,
                      priceFontSize: priceFontSize,
                      spacing: spacing,
                      radius: cardRadius,
                    ),
                    SizedBox(height: spacing),
                    _buildPaymentMethod(
                      cardPadding: cardPadding,
                      iconSize: iconSize,
                      sectionTitleSize: sectionTitleSize,
                      subtitleFontSize: subtitleFontSize,
                      radius: cardRadius,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// 🏨 HOTEL CARD
  Widget _buildHotelCard({
    required double imageSize,
    required double cardPadding,
    required double spacing,
    required double titleFontSize,
    required double subtitleFontSize,
    required double radius,
  }) {
    return Container(
      padding: EdgeInsets.all(cardPadding),
      decoration: _cardStyle(radius),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(radius * 0.8),
            child: Image.network(
              room.imageUrl,
              width: imageSize,
              height: imageSize,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  width: imageSize,
                  height: imageSize,
                  color: Colors.grey.shade200,
                  alignment: Alignment.center,
                  child: Icon(
                    Icons.broken_image,
                    color: Colors.grey,
                    size: imageSize * 0.4,
                  ),
                );
              },
            ),
          ),
          SizedBox(width: spacing),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  room.title,
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                    fontSize: titleFontSize,
                  ),
                ),
                SizedBox(height: spacing * 0.3),
                Text(
                  room.location,
                  style: TextStyle(
                    color: Colors.grey,
                    fontSize: subtitleFontSize,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 📅 DETALLES DEL VIAJE
  Widget _buildTripDetails(
    String dates,
    String guests, {
    required double cardPadding,
    required double sectionTitleSize,
    required double spacing,
    required double iconSize,
    required double labelSize,
    required double valueSize,
    required double radius,
  }) {
    return Container(
      padding: EdgeInsets.all(cardPadding),
      decoration: _cardStyle(radius),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "DETALLES DEL VIAJE",
            style: TextStyle(
              color: Colors.black,
              fontWeight: FontWeight.bold,
              fontSize: sectionTitleSize,
            ),
          ),
          SizedBox(height: spacing),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _detailItem(
                  Icons.calendar_today,
                  "Fechas",
                  dates,
                  iconSize: iconSize,
                  labelSize: labelSize,
                  valueSize: valueSize,
                ),
              ),
              SizedBox(width: spacing * 0.8),
              Expanded(
                child: _detailItem(
                  Icons.people,
                  "Huéspedes",
                  guests,
                  iconSize: iconSize,
                  labelSize: labelSize,
                  valueSize: valueSize,
                ),
              ),
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
    double total, {
    required String currencyTag,
    required double cardPadding,
    required double sectionTitleSize,
    required double priceFontSize,
    required double spacing,
    required double radius,
  }) {
    return Container(
      padding: EdgeInsets.all(cardPadding),
      decoration: _cardStyle(radius),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                "DESGLOSE DE PRECIOS",
                style: TextStyle(
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                  fontSize: sectionTitleSize,
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(
                  horizontal: cardPadding * 0.8,
                  vertical: cardPadding * 0.35,
                ),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(radius * 0.7),
                ),
                child: Text(
                  currencyTag,
                  style: TextStyle(
                    color: Colors.black,
                    fontSize: priceFontSize * 0.75,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: spacing),
          _priceRow(
            "$pricePerNight US\$ x $nights noches",
            "${subtotal.toStringAsFixed(0)} US\$",
            fontSize: priceFontSize,
          ),
          _priceRow(
            "Impuestos y cargos",
            "${taxes.toStringAsFixed(0)} US\$",
            fontSize: priceFontSize,
          ),
          SizedBox(height: spacing * 0.6),
          Divider(height: 1.5, color: Colors.grey.shade300),
          SizedBox(height: spacing * 0.6),
          _priceRow(
            "Total",
            "${total.toStringAsFixed(0)} US\$",
            isBold: true,
            fontSize: priceFontSize,
          ),
        ],
      ),
    );
  }

  /// 💳 MÉTODO DE PAGO
  Widget _buildPaymentMethod({
    required double cardPadding,
    required double iconSize,
    required double sectionTitleSize,
    required double subtitleFontSize,
    required double radius,
  }) {
    return Container(
      padding: EdgeInsets.all(cardPadding),
      decoration: _cardStyle(radius),
      child: Row(
        children: [
          Container(
            width: iconSize * 2.3,
            height: iconSize * 1.7,
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          SizedBox(width: cardPadding * 0.9),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Método de Pago",
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                    fontSize: sectionTitleSize,
                  ),
                ),
                SizedBox(height: cardPadding * 0.3),
                Text(
                  "Visa terminada en •••• 4242",
                  style: TextStyle(
                    color: Colors.grey,
                    fontSize: subtitleFontSize,
                  ),
                ),
              ],
            ),
          ),
          Icon(Icons.chevron_right, size: iconSize + 8),
        ],
      ),
    );
  }

  String _currencyCodeForLocale(BuildContext context, AppLocalizations l10n) {
    final locale = Localizations.localeOf(context);
    if (locale.countryCode == 'CO' || locale.languageCode == 'es') {
      return l10n.currencyCodeCOP;
    }
    return l10n.currencyCodeUSD;
  }

  BoxDecoration _cardStyle(double radius) {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(color: Colors.grey.shade200),
    );
  }

  Widget _detailItem(
    IconData icon,
    String title,
    String value, {
    required double iconSize,
    required double labelSize,
    required double valueSize,
  }) {
    return Row(
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: iconSize, color: Colors.grey),
                const SizedBox(width: 10),
                Text(
                  title,
                  style: TextStyle(color: Colors.grey, fontSize: labelSize),
                ),
              ],
            ),
            const SizedBox(height: 3),
            Text(
              value,
              style: TextStyle(
                color: Colors.black,
                fontWeight: FontWeight.bold,
                fontSize: valueSize,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _priceRow(
    String title,
    String value, {
    bool isBold = false,
    required double fontSize,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: TextStyle(
              color: isBold ? Colors.black : Colors.grey,
              fontSize: fontSize,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              color: Colors.black,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: fontSize,
            ),
          ),
        ],
      ),
    );
  }
}
