import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../services/user_service.dart';
import '../view_models/reservations_list_view_model.dart';
import '../widgets/reservation_card.dart';
import '../widgets/reservation_card_skeleton.dart';
import 'reservation_detail_view.dart';

class ReservationsListView extends StatefulWidget {
  const ReservationsListView({super.key});

  @override
  State<ReservationsListView> createState() => _ReservationsListViewState();
}

class _ReservationsListViewState extends State<ReservationsListView> {
  @override
  void initState() {
    super.initState();
    _loadReservations();
  }

  Future<void> _loadReservations() async {
    final userService = context.read<UserService>();
    final listViewModel = context.read<ReservationsListViewModel>();
    final userId = await userService.getUserId();
    listViewModel.loadReservations(userId);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Consumer<ReservationsListViewModel>(
          builder: (context, viewModel, child) {
            if (viewModel.isLoading && viewModel.reservations.isEmpty) {
              return _buildSkeletonLoader(l10n, theme);
            }

            return RefreshIndicator(
              onRefresh: () async {
                final userId = await context.read<UserService>().getUserId();
                await viewModel.loadReservations(userId);
              },
              child: CustomScrollView(
                slivers: [
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(24, 32, 24, 24),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (viewModel.isOffline)
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.symmetric(
                                vertical: 8,
                                horizontal: 16,
                              ),
                              margin: const EdgeInsets.only(bottom: 16),
                              decoration: BoxDecoration(
                                color: Colors.orange.shade100,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                l10n.offlineWarning,
                                style: TextStyle(
                                  color: Colors.orange.shade900,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          Text(
                            l10n.myReservationsTitle,
                            style: theme.textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.black,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            l10n.myReservationsSubtitle,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  _buildSectionHeader(l10n.upcomingReservationsSection),
                  if (viewModel.upcomingReservations.isEmpty)
                    _buildEmptyState(l10n.noUpcomingReservations)
                  else
                    SliverList(
                      delegate: SliverChildBuilderDelegate((context, index) {
                        final reservation =
                            viewModel.upcomingReservations[index];
                        return ReservationCard(
                          reservation: reservation,
                          onTap: () =>
                              _navigateToDetail(context, reservation.id),
                        );
                      }, childCount: viewModel.upcomingReservations.length),
                    ),
                  const SliverToBoxAdapter(child: SizedBox(height: 24)),
                  _buildSectionHeader(l10n.pastReservationsSection),
                  if (viewModel.pastReservations.isEmpty)
                    _buildEmptyState(l10n.noPastReservations)
                  else
                    SliverList(
                      delegate: SliverChildBuilderDelegate((context, index) {
                        final reservation = viewModel.pastReservations[index];
                        return ReservationCard(
                          reservation: reservation,
                          isPast: true,
                          onTap: () =>
                              _navigateToDetail(context, reservation.id),
                        );
                      }, childCount: viewModel.pastReservations.length),
                    ),
                  const SliverToBoxAdapter(child: SizedBox(height: 32)),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
        child: Text(
          title,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w900,
            letterSpacing: 1.2,
            color: Colors.black,
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState(String message) {
    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
        child: Center(
          child: Text(
            message,
            style: const TextStyle(
              color: Colors.grey,
              fontStyle: FontStyle.italic,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }

  Widget _buildSkeletonLoader(AppLocalizations l10n, ThemeData theme) {
    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 32, 24, 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.myReservationsTitle,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.black,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  l10n.myReservationsSubtitle,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ),
        ),
        _buildSectionHeader(l10n.upcomingReservationsSection),
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) => const ReservationCardSkeleton(),
            childCount: 2,
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 24)),
        _buildSectionHeader(l10n.pastReservationsSection),
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) => const ReservationCardSkeleton(isPast: true),
            childCount: 3,
          ),
        ),
      ],
    );
  }

  void _navigateToDetail(BuildContext context, String reservationId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            ReservationDetailView(reservationId: reservationId),
      ),
    );
  }
}
