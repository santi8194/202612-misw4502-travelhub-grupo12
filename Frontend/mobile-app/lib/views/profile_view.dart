import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../view_models/user_preferences_view_model.dart';

const List<String> _kCountries = [
  'Colombia',
  'USA',
  'Perú',
  'Ecuador',
  'México',
  'Chile',
  'Argentina',
];

class ProfileView extends StatefulWidget {
  const ProfileView({super.key});

  @override
  State<ProfileView> createState() => _ProfileViewState();
}

class _ProfileViewState extends State<ProfileView> {
  String _version = '';

  @override
  void initState() {
    super.initState();
    _loadVersion();
  }

  Future<void> _loadVersion() async {
    final packageInfo = await PackageInfo.fromPlatform();
    if (mounted) {
      setState(() {
        _version = packageInfo.version;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final prefs = context.watch<UserPreferencesViewModel>();
    final screenWidth = MediaQuery.of(context).size.width;
    final scale = (screenWidth / 390).clamp(0.8, 1.4);
    final bodyPadding = (24 * scale).clamp(18.0, 32.0);
    final titleFontSize = (16 * scale).clamp(14.0, 18.0);
    final labelFontSize = (14 * scale).clamp(13.0, 16.0);
    final cardRadius = (18 * scale).clamp(16.0, 22.0);
    final cardPadding = (16 * scale).clamp(14.0, 22.0);

    final canPop = ModalRoute.of(context)?.canPop ?? false;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.profileTitleView),
        leading: canPop
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => Navigator.of(context).pop(),
              )
            : null,
        automaticallyImplyLeading: false,
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          return SingleChildScrollView(
            padding: EdgeInsets.all(bodyPadding),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: constraints.maxHeight - (bodyPadding * 2),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Center(
                        child: Padding(
                          padding: EdgeInsets.symmetric(vertical: 32.0),
                          child: Icon(
                            Icons.person_outline,
                            size: 100,
                            color: Colors.grey,
                          ),
                        ),
                      ),
                      _buildSectionCard(
                        context: context,
                        cardRadius: cardRadius,
                        cardPadding: cardPadding,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              l10n.countryLabel,
                              style: TextStyle(
                                fontSize: titleFontSize,
                                fontWeight: FontWeight.w600,
                                color: Colors.black87,
                              ),
                            ),
                            SizedBox(height: cardPadding / 2),
                            DropdownButtonFormField<String>(
                              initialValue: prefs.country,
                              isExpanded: true,
                              decoration: InputDecoration(
                                contentPadding: EdgeInsets.symmetric(
                                  horizontal: cardPadding,
                                  vertical: cardPadding / 2,
                                ),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(
                                    cardRadius / 2,
                                  ),
                                ),
                              ),
                              hint: Text(
                                l10n.countryNotSet,
                                style: TextStyle(
                                  fontSize: labelFontSize,
                                  color: Colors.black45,
                                ),
                              ),
                              items: _kCountries
                                  .map(
                                    (c) => DropdownMenuItem(
                                      value: c,
                                      child: Text(
                                        c,
                                        style: TextStyle(
                                          fontSize: labelFontSize,
                                        ),
                                      ),
                                    ),
                                  )
                                  .toList(),
                              onChanged: (value) {
                                context
                                    .read<UserPreferencesViewModel>()
                                    .setCountry(value);
                              },
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        l10n.profileVersion(_version),
                        style: Theme.of(
                          context,
                        ).textTheme.bodySmall?.copyWith(color: Colors.grey),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSectionCard({
    required BuildContext context,
    required double cardRadius,
    required double cardPadding,
    required Widget child,
  }) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(cardRadius),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      padding: EdgeInsets.all(cardPadding),
      child: child,
    );
  }
}
