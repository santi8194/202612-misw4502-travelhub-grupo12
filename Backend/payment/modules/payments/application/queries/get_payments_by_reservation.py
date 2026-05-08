class GetPaymentsByReservation:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, reservation_id: str):
        payments = self.repository.obtain_all_by_reservation(reservation_id)
        return [
            {
                "id": p.id,
                "reservation_id": p.reservation_id,
                "amount": p.amount,
                "currency": p.currency,
                "state": p.state
            }
            for p in payments
        ]
