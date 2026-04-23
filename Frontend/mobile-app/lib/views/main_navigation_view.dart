import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../widgets/app_bottom_nav_bar.dart';
import 'busqueda_view.dart';
import 'profile_view.dart';

class MainNavigationView extends StatefulWidget {
  final int initialIndex;
  const MainNavigationView({super.key, this.initialIndex = 0});

  @override
  State<MainNavigationView> createState() => _MainNavigationViewState();
}

class _MainNavigationViewState extends State<MainNavigationView> {
  late int _selectedIndex = widget.initialIndex;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    final List<Widget> pages = [
      const BusquedaView(),
      Center(child: Text(l10n.navBookings)),
      const ProfileView(),
    ];

    return Scaffold(
      body: pages[_selectedIndex],
      bottomNavigationBar: AppBottomNavBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
      ),
    );
  }
}
