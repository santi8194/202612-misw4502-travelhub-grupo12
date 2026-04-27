import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../models/categoria_habitacion.dart';
import '../models/country_tax.dart';
import '../services/catalog_service.dart';
import '../view_models/confirm_reservation_view_model.dart';
import '../view_models/user_preferences_view_model.dart';
import '../widgets/app_bottom_nav_bar.dart';

class ConfirmReservationView extends StatelessWidget {
  final String location;
  final String categoryId;
  final DateTimeRange dateRange;
  final int guests;
  final CatalogService? catalogService;

  const ConfirmReservationView({
    super.key,
    required this.location,
    required this.categoryId,
    required this.dateRange,
    required this.guests,
    this.catalogService,
  });

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ConfirmReservationViewModel(
        location: location,
        categoryId: categoryId,
        selectedDateRange: dateRange,
        guests: guests,
        catalogService: catalogService,
      ),
      child: Consumer<ConfirmReservationViewModel>(
        builder: (context, viewModel, child) {
          final l10n = AppLocalizations.of(context)!;
          final locale = Localizations.localeOf(context).toString();
          final monthFormatter = DateFormat.MMM(locale);

          if (viewModel.isLoading) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }

          if (viewModel.errorMessage != null || viewModel.categoria == null) {
            return Scaffold(
              appBar: AppBar(
                leading: IconButton(
                  icon: const Icon(Icons.arrow_back, color: Colors.black),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
              body: Center(
                child: Text(
                  viewModel.errorMessage ?? 'Error al cargar la categoría',
                ),
              ),
            );
          }

          final categoria = viewModel.categoria!;
          final nights = dateRange.duration.inDays;

          // Delegate all price/currency computation to the ViewModel
          final fallbackCurrency =
              (Localizations.localeOf(context).languageCode == 'es')
              ? l10n.currencyCodeCOP
              : l10n.currencyCodeUSD;
          final breakdown = viewModel.computePriceBreakdown(
            nights: nights,
            country: context.watch<UserPreferencesViewModel>().country,
            taxConfig: context.read<Map<String, CountryTax>>(),
            fallbackCurrency: fallbackCurrency,
            localeLanguageCode: Localizations.localeOf(context).languageCode,
          )!;

          final start = dateRange.start;
          final end = dateRange.end;

          final formattedDates = start.month == end.month
              ? '${start.day} - ${end.day} ${monthFormatter.format(start).toUpperCase()}'
              : '${start.day} ${monthFormatter.format(start).toUpperCase()} - ${end.day} ${monthFormatter.format(end).toUpperCase()}';

          final screenWidth = MediaQuery.of(context).size.width;
          final scale = screenWidth / 390;
          final cardPadding = (13 * scale).clamp(12.0, 20.0);
          final imageSize = (76 * scale).clamp(66.0, 84.0);
          final titleFontSize = (16 * scale).clamp(14.0, 18.0);
          final subtitleFontSize = (14 * scale).clamp(12.0, 16.0);
          final sectionTitleSize = (14 * scale).clamp(13.0, 16.0);
          final detailLabelSize = (13 * scale).clamp(12.0, 15.0);
          final detailValueSize = (14 * scale).clamp(13.0, 16.0);
          final priceFontSize = (14 * scale).clamp(13.0, 16.0);
          final buttonFontSize = (17 * scale).clamp(15.0, 19.0);
          final buttonHeight = (56 * scale).clamp(50.0, 62.0);
          final iconSize = (15 * scale).clamp(14.0, 20.0);
          final spacing = (16 * scale).clamp(12.0, 20.0);
          final cardRadius = (18 * scale).clamp(16.0, 22.0);
          final bodyPadding = (22 * scale).clamp(18.0, 32.0);
          final cardGap = (32 * scale).clamp(24.0, 40.0);

          return Scaffold(
            backgroundColor: Colors.white,
            appBar: AppBar(
              backgroundColor: Colors.white,
              elevation: 0,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, color: Colors.black),
                onPressed: () => Navigator.pop(context),
              ),
              title: Text(
                l10n.confirmReservationTitle,
                style: const TextStyle(
                  color: Colors.black,
                  fontWeight: FontWeight.bold,
                  fontSize: 20,
                ),
              ),
              centerTitle: true,
            ),

            bottomNavigationBar: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Padding(
                  padding: EdgeInsets.symmetric(
                    horizontal: bodyPadding,
                    vertical: bodyPadding * 0.6,
                  ),
                  child: SizedBox(
                    width: double.infinity,
                    height: buttonHeight,
                    child: ElevatedButton(
                      onPressed: viewModel.isConfirming
                          ? null
                          : () async {
                              final confirmed = await viewModel
                                  .confirmReservation();
                              if (confirmed && context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      l10n.reservationSuccessMessage,
                                    ),
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
                              l10n.confirmReservationButton,
                              style: TextStyle(
                                fontSize: buttonFontSize,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ),
                ),
                const AppBottomNavBar(currentIndex: 1, onTap: null),
              ],
            ),

            body: Container(
              color: Colors.white,
              child: SingleChildScrollView(
                padding: EdgeInsets.only(
                  top: bodyPadding,
                  right: bodyPadding,
                  bottom: bodyPadding,
                  left: bodyPadding,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildHotelCard(
                      location: location,
                      categoria: categoria,
                      imageSize: imageSize,
                      cardPadding: cardPadding,
                      spacing: spacing,
                      titleFontSize: titleFontSize,
                      subtitleFontSize: subtitleFontSize,
                      radius: cardRadius,
                    ),
                    SizedBox(height: cardGap),
                    _buildTripDetails(
                      formattedDates,
                      l10n.guestCountLabel(guests),
                      cardPadding: cardPadding,
                      sectionTitleSize: sectionTitleSize,
                      spacing: spacing,
                      iconSize: iconSize,
                      labelSize: detailLabelSize,
                      valueSize: detailValueSize,
                      radius: cardRadius,
                      l10n: l10n,
                    ),
                    SizedBox(height: cardGap),
                    _buildPriceBreakdown(
                      nights,
                      breakdown,
                      cardPadding: cardPadding,
                      sectionTitleSize: sectionTitleSize,
                      priceFontSize: priceFontSize,
                      spacing: spacing,
                      radius: cardRadius,
                      l10n: l10n,
                    ),
                    SizedBox(height: cardGap),
                    _buildPaymentMethod(
                      cardPadding: cardPadding,
                      iconSize: iconSize,
                      sectionTitleSize: sectionTitleSize,
                      subtitleFontSize: subtitleFontSize,
                      radius: cardRadius,
                      l10n: l10n,
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
    required String location,
    required CategoriaHabitacion categoria,
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
              categoria.fotoPortadaUrl,
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
                  categoria.nombreComercial,
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                    fontSize: titleFontSize,
                  ),
                ),
                SizedBox(height: spacing * 0.3),
                Text(
                  location,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
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
    String guestLabel, {
    required double cardPadding,
    required double sectionTitleSize,
    required double spacing,
    required double iconSize,
    required double labelSize,
    required double valueSize,
    required double radius,
    required AppLocalizations l10n,
  }) {
    return Container(
      padding: EdgeInsets.all(cardPadding),
      decoration: _cardStyle(radius),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.tripDetailsTitle,
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
                  l10n.reservationDatesLabel,
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
                  l10n.reservationGuestsLabel,
                  guestLabel,
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
    PriceBreakdown breakdown, {
    required double cardPadding,
    required double sectionTitleSize,
    required double priceFontSize,
    required double spacing,
    required double radius,
    required AppLocalizations l10n,
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
                l10n.priceBreakdownTitle,
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
                  breakdown.currencyTag,
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
            "${breakdown.fmtPricePerNight} x ${l10n.nightsLabel(nights)}",
            breakdown.fmtSubtotal,
            fontSize: priceFontSize,
          ),
          _priceRow(
            l10n.taxesAndCharges,
            breakdown.fmtTaxesAndCharges,
            fontSize: priceFontSize,
          ),

          SizedBox(height: spacing * 0.6),
          Divider(height: 1.5, color: Colors.grey.shade300),
          SizedBox(height: spacing * 0.6),
          _priceRow(
            l10n.totalPrice,
            breakdown.fmtTotal,
            isBold: true,
            fontSize: priceFontSize,
          ),
          if (breakdown.taxNote != null) ...[
            SizedBox(height: spacing * 0.6),
            Text(
              breakdown.taxNote!,
              style: TextStyle(
                color: Colors.grey,
                fontSize: priceFontSize * 0.82,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
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
    required AppLocalizations l10n,
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
                  l10n.paymentMethod,
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                    fontSize: sectionTitleSize,
                  ),
                ),
                SizedBox(height: cardPadding * 0.3),
                Text(
                  l10n.cardEnding,
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
