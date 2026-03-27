import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';

class MainNavigationView extends StatefulWidget {
  const MainNavigationView({super.key});

  @override
  State<MainNavigationView> createState() => _MainNavigationViewState();
}

class _MainNavigationViewState extends State<MainNavigationView> {
  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    final List<Widget> pages = [
      Center(child: Text(l10n.homeTitle)),
      Center(child: Text(l10n.searchTitle)),
      Center(child: Text(l10n.bookingsTitle)),
      Center(child: Text(l10n.profileTitle)),
    ];

    return Scaffold(
      body: pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.blue[800],
        unselectedItemColor: Colors.grey,
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.home),
            label: l10n.navHome,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.search),
            label: l10n.navSearch,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.calendar_today),
            label: l10n.navBookings,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person),
            label: l10n.navProfile,
          ),
        ],
      ),
    );
  }
}
