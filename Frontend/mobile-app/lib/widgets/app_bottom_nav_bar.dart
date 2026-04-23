import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../views/main_navigation_view.dart';

class AppBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int>? onTap;

  const AppBottomNavBar({super.key, this.currentIndex = 0, this.onTap});

  void _handleTap(BuildContext context, int index) {
    if (onTap != null) {
      onTap!(index);
    } else {
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => MainNavigationView(initialIndex: index),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: (index) => _handleTap(context, index),
      type: BottomNavigationBarType.fixed,
      selectedItemColor: Theme.of(
        context,
      ).bottomNavigationBarTheme.selectedItemColor,
      unselectedItemColor: Theme.of(
        context,
      ).bottomNavigationBarTheme.unselectedItemColor,
      showSelectedLabels: true,
      showUnselectedLabels: true,
      items: [
        BottomNavigationBarItem(
          icon: const Icon(Icons.search),
          label: l10n.navSearch,
        ),
        BottomNavigationBarItem(
          icon: const Icon(Icons.card_travel),
          label: l10n.navBookings,
        ),
        BottomNavigationBarItem(
          icon: const Icon(Icons.person_outline),
          label: l10n.navProfile,
        ),
      ],
    );
  }
}
