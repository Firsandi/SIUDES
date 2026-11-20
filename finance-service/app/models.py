import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Invoice(Base):
    """Invoice generated from usage.recorded events."""

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    customer_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    unit_type: Mapped[str] = mapped_column(String(32), nullable=False)
    usage_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tariff_rate: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="UNPAID", server_default="UNPAID"
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    payment_log: Mapped["PaymentLog | None"] = relationship(
        back_populates="invoice", uselist=False
    )


class PaymentLog(Base):
    """Immutable audit log of invoice payments."""

    __tablename__ = "payment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoices.id"), unique=True, nullable=False
    )
    paid_by_role: Mapped[str] = mapped_column(String(32), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    invoice: Mapped["Invoice"] = relationship(back_populates="payment_log")
