from sqlalchemy import Boolean, Column, Float, String
from .database import Base

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    reservation_id = Column(String)
    reference = Column(String, unique=True, index=True)
    amount = Column(Float)
    currency = Column(String)
    state = Column(String)
    wompi_transaction_id = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    event_published = Column(Boolean, default=False)
