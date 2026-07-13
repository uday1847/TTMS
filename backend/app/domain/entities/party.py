from decimal import Decimal

from sqlalchemy import Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import BaseEntity


class Party(BaseEntity):
    """
    Represents customer accounts or suppliers who generate trips and invoices.
    """
    __tablename__ = "parties"

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    tax_identifier: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    billing_address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    contact_person: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    contact_phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    outstanding_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    payment_terms_days: Mapped[int] = mapped_column(
        nullable=False,
        default=30,
    )

    party_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,  # e.g., 'CUSTOMER', 'SUPPLIER', 'INTERNAL'
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_parties_code",
            "code",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "uq_parties_tax_identifier",
            "tax_identifier",
            unique=True,
            postgresql_where="tax_identifier IS NOT NULL AND deleted_at IS NULL",
        ),
    )
