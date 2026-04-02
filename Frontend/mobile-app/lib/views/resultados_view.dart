import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../l10n/app_localizations.dart';
import '../view_models/search_view_model.dart';

class ResultadosView extends StatefulWidget {
  const ResultadosView({super.key});

  @override
  State<ResultadosView> createState() => _ResultadosViewState();
}

class _ResultadosViewState extends State<ResultadosView> {
  String _getSubtitle(SearchViewModel vm) {
    String destination = vm.destinationQuery.isEmpty ? 'CUALQUIER DESTINO' : vm.destinationQuery.toUpperCase();
    
    String dates = '';
    if (vm.selectedDateRange != null) {
      final start = vm.selectedDateRange!.start;
      final end = vm.selectedDateRange!.end;
      final monthNames = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
      if (start.month == end.month) {
        dates = '${start.day} - ${end.day} ${monthNames[start.month - 1]}';
      } else {
        dates = '${start.day} ${monthNames[start.month - 1]} - ${end.day} ${monthNames[end.month - 1]}';
      }
    } else {
      dates = 'FECHAS ABIERTAS';
    }

    String guests = '${vm.guestCount} HUÉSPEDE${vm.guestCount > 1 ? 'S' : ''}';
    
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
              style: const TextStyle(color: Colors.black, fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              _getSubtitle(vm),
              style: const TextStyle(color: Colors.grey, fontSize: 10, letterSpacing: 1.2, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: vm.isSearching 
        ? const Center(child: CircularProgressIndicator())
        : Column(
            children: [
              // Cached results banner
              if (vm.isFromCache)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  color: Colors.amber.shade50,
                  child: Row(
                    children: [
                      Icon(Icons.cached_rounded, size: 16, color: Colors.amber.shade800),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Mostrando resultados en caché. Se actualizarán al recuperar conexión.',
                          style: TextStyle(fontSize: 12, color: Colors.amber.shade900, fontWeight: FontWeight.w500),
                        ),
                      ),
                    ],
                  ),
                ),
              Expanded(
                child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
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
                  color: Colors.black.withOpacity(0.04),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(30)),
                  child: Stack(
                    children: [
                      Image.network(
                        hotel.imageUrl,
                        height: 220,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                      if (hotel.isSpecialOffer)
                        Positioned(
                          top: 16,
                          left: 16,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(20),
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
                        style: theme.textTheme.displayMedium?.copyWith(
                          fontSize: 22,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Icon(Icons.location_on_outlined, size: 18, color: Colors.grey),
                          const SizedBox(width: 4),
                          Text(
                            hotel.location,
                            style: const TextStyle(color: Colors.grey, fontSize: 14),
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
