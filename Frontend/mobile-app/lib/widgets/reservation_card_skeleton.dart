import 'package:flutter/material.dart';

import 'skeleton_loader.dart';

class ReservationCardSkeleton extends StatelessWidget {
  final bool isPast;

  const ReservationCardSkeleton({super.key, this.isPast = false});

  @override
  Widget build(BuildContext context) {
    return isPast ? _buildPastCardSkeleton() : _buildUpcomingCardSkeleton();
  }

  Widget _buildUpcomingCardSkeleton() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Skeleton(height: 24, width: 200),
                    SizedBox(height: 8),
                    Skeleton(height: 16, width: 150),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Skeleton(height: 56, width: 56, borderRadius: 12),
            ],
          ),
          const SizedBox(height: 24),
          const Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Skeleton(height: 12, width: 60),
                    SizedBox(height: 8),
                    Skeleton(height: 18, width: 100),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Skeleton(height: 12, width: 80),
                    SizedBox(height: 8),
                    Skeleton(height: 18, width: 80),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: List.generate(
                  2,
                  (index) => const Padding(
                    padding: EdgeInsets.only(right: 8),
                    child: Skeleton(height: 32, width: 32, borderRadius: 16),
                  ),
                ),
              ),
              const Skeleton(height: 20, width: 100),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPastCardSkeleton() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF4F5F9),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.black.withOpacity(0.05)),
      ),
      child: const Row(
        children: [
          Skeleton(height: 56, width: 56, borderRadius: 12),
          SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Skeleton(height: 18, width: 150),
                SizedBox(height: 8),
                Skeleton(height: 14, width: 100),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Skeleton(height: 18, width: 60),
              SizedBox(height: 8),
              Skeleton(height: 12, width: 40),
            ],
          ),
        ],
      ),
    );
  }
}
