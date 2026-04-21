import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../view_models/search_view_model.dart';
import 'confirm_reservation_view.dart';

class ResultadosView extends StatefulWidget {
  const ResultadosView({super.key});

  @override
  State<ResultadosView> createState() => _ResultadosViewState();
}

class _ResultadosViewState extends State<ResultadosView> {
  Widget _buildHotelImage(String imageUrl) {
    return Container(
      height: 220,
      width: double.infinity,
      color: Colors.grey.shade200,
      child: imageUrl.isEmpty
          ? _buildImagePlaceholder()
          : Image.network(
              imageUrl,
              height: 220,
              width: double.infinity,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return _buildImagePlaceholder();
              },
              loadingBuilder: (context, child, loadingProgress) {
                if (loadingProgress == null) return child;
                return _buildImagePlaceholder(showLoader: true);
              },
            ),
    );
  }

  Widget _buildImagePlaceholder({bool showLoader = false}) {
    return Container(
      color: Colors.grey.shade200,
      alignment: Alignment.center,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (showLoader)
            const SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(strokeWidth: 2.5),
            )
          else
            Icon(
              Icons.hotel_outlined,
              size: 42,
              color: Colors.grey.shade500,
            ),
          const SizedBox(height: 12),
          Text(
            'Imagen no disponible',
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  String _getSubtitle(SearchViewModel vm) {
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).toString();
    final monthFormatter = DateFormat.MMM(locale);

    String destination = vm.destinationQuery.isEmpty
        ? l10n.anyDestination
        : vm.destinationQuery.toUpperCase();

    String dates = '';
    if (vm.selectedDateRange != null) {
      final start = vm.selectedDateRange!.start;
      final end = vm.selectedDateRange!.end;

      if (start.month == end.month) {
        dates =
            '${start.day} - ${end.day} ${monthFormatter.format(start).toUpperCase()}';
      } else {
        dates =
            '${start.day} ${monthFormatter.format(start).toUpperCase()} - ${end.day} ${monthFormatter.format(end).toUpperCase()}';
      }
    } else {
      dates = l10n.openDates;
    }

    String guests = l10n.guestCountLabel(vm.guestCount).toUpperCase();

    return '$destination • $dates • $guests';
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final vm = context.watch<SearchViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: Padding(
          padding: const EdgeInsets.only(left: 16.0),
          child: CircleAvatar(
            backgroundColor: Colors.white, // greyish border
            child: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.black87),
              onPressed: () => Navigator.pop(context),
            ),
          ),
        ),
        title: Column(
          children: [
            Text(
              l10n.resultsTitle,
              style: const TextStyle(
                color: Colors.black,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              _getSubtitle(vm),
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: vm.isSearching
          ? const Center(child: CircularProgressIndicator())
          : vm.hasNoResults
          ? Padding(
              padding: const EdgeInsets.symmetric(horizontal: 48.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.search_off_rounded,
                      size: 64,
                      color: Colors.blue.shade300,
                    ),
                  ),
                  const SizedBox(height: 32),
                  Text(
                    l10n.noResultsTitle,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.displayMedium?.copyWith(
                      fontSize: 24,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    l10n.noResultsMessage,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontSize: 16,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      child: Text(l10n.tryAnotherSearch),
                    ),
                  ),
                ],
              ),
            )
          : Column(
              children: [
                // Cached results banner
                if (vm.isFromCache)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 10,
                    ),
                    color: Colors.amber.shade50,
                    child: Row(
                      children: [
                        Icon(
                          Icons.cached_rounded,
                          size: 16,
                          color: Colors.amber.shade800,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            l10n.cachedResultsBanner,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.amber.shade900,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 16,
                    ),
                    itemCount: vm.searchResults.length,
                    itemBuilder: (context, index) {
                      final hotel = vm.searchResults[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(30),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.04),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            ClipRRect(
                              borderRadius: const BorderRadius.vertical(
                                top: Radius.circular(30),
                              ),
                              child: Stack(
                                children: [
                                  _buildHotelImage(hotel.imageUrl),
                                  if (hotel.isSpecialOffer)
                                    Positioned(
                                      top: 16,
                                      left: 16,
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 16,
                                          vertical: 8,
                                        ),
                                        decoration: BoxDecoration(
                                          color: Colors.white.withValues(
                                            alpha: 0.2,
                                          ),
                                          borderRadius: BorderRadius.circular(
                                            20,
                                          ),
                                        ),
                                        child: Text(
                                          l10n.specialOffer,
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            Padding(
                              padding: const EdgeInsets.all(24.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    hotel.title,
                                    style: theme.textTheme.displayMedium
                                        ?.copyWith(fontSize: 22),
                                  ),
                                  const SizedBox(height: 8),
                                  Row(
                                    children: [
                                      const Icon(
                                        Icons.location_on_outlined,
                                        size: 18,
                                        color: Colors.grey,
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        hotel.location,
                                        style: const TextStyle(
                                          color: Colors.grey,
                                          fontSize: 14,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 20),
                                  Wrap(
                                    spacing: 16,
                                    runSpacing: 8,
                                    children: hotel.amenities.map((amenity) {
                                      return Text(
                                        amenity,
                                        style: TextStyle(
                                          color: Colors.grey[800],
                                          fontSize: 10,
                                          fontWeight: FontWeight.bold,
                                          letterSpacing: 1.2,
                                        ),
                                      );
                                    }).toList(),
                                  ),
                                  const SizedBox(height: 24),
                                  SizedBox(
                                    width: double.infinity,
                                    height: 48,
                                    child: ElevatedButton(
                                      onPressed: () {
                                        final dateRange =
                                            vm.selectedDateRange ??
                                            DateTimeRange(
                                              start: DateTime.now(),
                                              end: DateTime.now().add(
                                                const Duration(days: 1),
                                              ),
                                            );
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (context) =>
                                                ConfirmReservationView(
                                                  room: hotel,
                                                  dateRange: dateRange,
                                                  guests: vm.guestCount,
                                                ),
                                          ),
                                        );
                                      },
                                      child: Text(
                                        l10n.confirmReservationButton,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ), // Expanded
              ], // Column children
            ), // Column
    );
  }
}
