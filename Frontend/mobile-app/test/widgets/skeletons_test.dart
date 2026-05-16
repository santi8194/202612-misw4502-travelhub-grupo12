import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/widgets/reservation_card_skeleton.dart';
import 'package:travel_hub/widgets/skeleton_loader.dart';

void main() {
  testWidgets('Skeleton renders correctly', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: Skeleton(width: 100, height: 20, borderRadius: 8)),
      ),
    );

    expect(find.byType(Skeleton), findsOneWidget);
    final container = tester.widget<Container>(
      find.descendant(
        of: find.byType(Skeleton),
        matching: find.byType(Container),
      ),
    );
    expect((container.decoration as BoxDecoration).borderRadius, isNotNull);
  });

  testWidgets('ReservationCardSkeleton renders correctly', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ReservationCardSkeleton())),
    );

    expect(find.byType(ReservationCardSkeleton), findsOneWidget);
    expect(find.byType(Skeleton), findsAtLeast(3));
  });
}
