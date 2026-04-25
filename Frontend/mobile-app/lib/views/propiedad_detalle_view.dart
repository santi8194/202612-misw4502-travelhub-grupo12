import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../models/habitacion.dart';
import '../services/catalog_service.dart';
import 'confirm_reservation_view.dart';

class PropiedadDetalleView extends StatefulWidget {
  final Habitacion habitacion;
  final DateTimeRange? dateRange;
  final int guests;

  const PropiedadDetalleView({
    super.key,
    required this.habitacion,
    this.dateRange,
    required this.guests,
  });

  @override
  State<PropiedadDetalleView> createState() => _PropiedadDetalleViewState();
}

class _PropiedadDetalleViewState extends State<PropiedadDetalleView>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final CatalogService _catalogService = CatalogService();

  Map<String, dynamic>? _propertyDetail;
  bool _isLoading = true;
  String? _errorMessage;

  List<String> _galleryImages = [];
  List<Map<String, dynamic>> _amenities = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _fetchPropertyDetail();
  }

  Future<void> _fetchPropertyDetail() async {
    if (widget.habitacion.categoryId == null) {
      setState(() {
        _isLoading = false;
        _errorMessage = "No category ID available";
      });
      return;
    }

    try {
      final detail = await _catalogService.getPropertyDetail(
        widget.habitacion.categoryId!,
      );
      setState(() {
        _propertyDetail = detail;
        _isLoading = false;

        // Extract gallery
        final galeria = detail['galeria'] as List? ?? [];
        _galleryImages = galeria.map((m) => m['url_full'] as String).toList();
        if (_galleryImages.isEmpty) {
          _galleryImages = [widget.habitacion.imageUrl];
        }

        // Extract amenities
        _amenities =
            (detail['amenidades'] as List?)?.cast<Map<String, dynamic>>() ?? [];
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString();
      });
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _showFullScreenImage(BuildContext context, String imageUrl) {
    showDialog(
      context: context,
      barrierColor: Colors.black,
      builder: (context) => Scaffold(
        backgroundColor: Colors.black,
        body: Stack(
          children: [
            Center(
              child: InteractiveViewer(
                maxScale: 5.0,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(40),
                    child: Image.network(
                      imageUrl,
                      fit: BoxFit.contain,
                      width: double.infinity,
                    ),
                  ),
                ),
              ),
            ),
            Positioned(
              top: 60,
              right: 30,
              child: GestureDetector(
                onTap: () => Navigator.pop(context),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.close, color: Colors.white, size: 24),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_errorMessage != null && _propertyDetail == null) {
      return Scaffold(
        appBar: AppBar(),
        body: Center(child: Text("Error: $_errorMessage")),
      );
    }

    final property = _propertyDetail!['propiedad'];
    final category = _propertyDetail!['categoria'];

    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          CustomScrollView(
            slivers: [
              _buildHeader(context, l10n, property),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: _buildTabBar(l10n),
                ),
              ),
              SliverFillRemaining(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildInfoTab(l10n, theme, category),
                    _buildRoomsTab(l10n),
                  ],
                ),
              ),
            ],
          ),
          _buildBottomBar(l10n, theme, category),
        ],
      ),
    );
  }

  Widget _buildHeader(
    BuildContext context,
    AppLocalizations l10n,
    dynamic property,
  ) {
    final stars = property['estrellas'] as int? ?? 0;

    return SliverAppBar(
      expandedHeight: 300,
      pinned: true,
      backgroundColor: Colors.white,
      leading: Padding(
        padding: const EdgeInsets.all(8.0),
        child: CircleAvatar(
          backgroundColor: Colors.white.withValues(alpha: 0.3),
          child: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () => Navigator.pop(context),
          ),
        ),
      ),
      flexibleSpace: FlexibleSpaceBar(
        background: Stack(
          fit: StackFit.expand,
          children: [
            GestureDetector(
              onTap: () => _showFullScreenImage(context, _galleryImages.first),
              child: Image.network(_galleryImages.first, fit: BoxFit.cover),
            ),
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.3),
                    Colors.transparent,
                    Colors.black.withValues(alpha: 0.7),
                  ],
                ),
              ),
            ),
            Positioned(
              bottom: 24,
              left: 24,
              right: 24,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          'PREMIUM',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Row(
                        children: List.generate(
                          5,
                          (index) => Icon(
                            index < stars ? Icons.star : Icons.star_border,
                            color: Colors.amber,
                            size: 14,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    property['nombre'] ?? widget.habitacion.title,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(
                        Icons.location_on,
                        color: Colors.white70,
                        size: 16,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${property['ubicacion']['ciudad']}, ${property['ubicacion']['pais']}',
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabBar(AppLocalizations l10n) {
    return Container(
      height: 60,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFFF3F4F6),
        borderRadius: BorderRadius.circular(20),
      ),
      child: TabBar(
        controller: _tabController,
        indicator: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        labelColor: Colors.black,
        unselectedLabelColor: Colors.grey,
        dividerColor: Colors.transparent,
        indicatorSize: TabBarIndicatorSize.tab,
        labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        tabs: [
          Tab(text: l10n.propertyInfoTab),
          Tab(text: l10n.propertyRoomsTab),
        ],
      ),
    );
  }

  Widget _buildInfoTab(
    AppLocalizations l10n,
    ThemeData theme,
    dynamic category,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.aboutProperty,
            style: theme.textTheme.displayMedium?.copyWith(fontSize: 20),
          ),
          const SizedBox(height: 16),
          Text(
            category['descripcion'] ?? 'No hay descripción disponible.',
            style: const TextStyle(
              color: Colors.black54,
              height: 1.6,
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 32),
          Text(
            l10n.mainAmenities,
            style: theme.textTheme.displayMedium?.copyWith(fontSize: 20),
          ),
          const SizedBox(height: 16),
          _amenities.isEmpty
              ? const Text("No hay amenidades listadas.")
              : GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: 2.5,
                  ),
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _amenities.length,
                  itemBuilder: (context, index) {
                    final amenity = _amenities[index];
                    return _buildAmenityCard(
                      _getIconData(amenity['icono']),
                      amenity['nombre'].toUpperCase(),
                    );
                  },
                ),
          const SizedBox(height: 100), // Space for footer
        ],
      ),
    );
  }

  IconData _getIconData(String? iconName) {
    switch (iconName?.toLowerCase()) {
      case 'wifi':
        return Icons.wifi;
      case 'pool':
        return Icons.pool;
      case 'restaurant':
        return Icons.restaurant;
      case 'kitchen':
        return Icons.kitchen;
      case 'spa':
        return Icons.spa;
      case 'fitness_center':
        return Icons.fitness_center;
      case 'local_laundry_service':
        return Icons.local_laundry_service;
      case 'fireplace':
        return Icons.fireplace;
      case 'outdoor_grill':
        return Icons.outdoor_grill;
      case 'park':
        return Icons.park;
      default:
        return Icons.check_circle_outline;
    }
  }

  Widget _buildAmenityCard(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF9FAFB),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.black87),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRoomsTab(AppLocalizations l10n) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.roomGallery,
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          if (_galleryImages.isNotEmpty)
            GestureDetector(
              onTap: () => _showFullScreenImage(context, _galleryImages[0]),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(30),
                child: Image.network(
                  _galleryImages[0],
                  height: 250,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
            ),
          const SizedBox(height: 16),
          if (_galleryImages.length >= 3)
            Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () =>
                        _showFullScreenImage(context, _galleryImages[1]),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(20),
                      child: Image.network(
                        _galleryImages[1],
                        height: 150,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: GestureDetector(
                    onTap: () =>
                        _showFullScreenImage(context, _galleryImages[2]),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(20),
                      child: Image.network(
                        _galleryImages[2],
                        height: 150,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          const SizedBox(height: 100),
        ],
      ),
    );
  }

  Widget _buildBottomBar(
    AppLocalizations l10n,
    ThemeData theme,
    dynamic category,
  ) {
    final priceStr = category['precio_base']['monto'] as String? ?? '0';
    final price = double.tryParse(priceStr) ?? 0.0;

    return Positioned(
      bottom: 0,
      left: 0,
      right: 0,
      child: Container(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 20,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.totalPriceLabel,
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                  RichText(
                    text: TextSpan(
                      children: [
                        TextSpan(
                          text: '${price.toInt()} US\$',
                          style: theme.textTheme.displayMedium?.copyWith(
                            fontSize: 24,
                          ),
                        ),
                        TextSpan(
                          text: ' / noche',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFF9FAFB),
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                elevation: 4,
                shadowColor: Colors.black12,
              ),
              onPressed: () {
                final dateRange =
                    widget.dateRange ??
                    DateTimeRange(
                      start: DateTime.now(),
                      end: DateTime.now().add(const Duration(days: 1)),
                    );
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ConfirmReservationView(
                      location: widget.habitacion.location,
                      categoryId: widget.habitacion.categoryId ?? '',
                      dateRange: dateRange,
                      guests: widget.guests,
                    ),
                  ),
                );
              },
              child: Text(
                l10n.reserveNow,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
