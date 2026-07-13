from decimal import Decimal

from typing import TYPE_CHECKING

from sqlalchemy import Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.domain.entities.invoice import Invoice

from app.infrastructure.database.base import BaseEntity


class Party(BaseEntity):
    """
    Represents customer accounts, suppliers, brokers, or transporters
    who generate trips and invoices.
    """
    __tablename__ = "parties"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    party_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,  # e.g., 'CUSTOMER', 'SUPPLIER', 'BROKER', 'OTHER'
        index=True,
    )

    mobile_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    alternate_mobile: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    gst_number: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
        index=True,
    )

    pan_number: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    opening_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="party",
        lazy="selectin",
        foreign_keys="[Invoice.party_id]"
    )

    # Constraints and Indexes
    __table_args__ = (
        Index(
            "uq_parties_mobile_number",
            "mobile_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "uq_parties_gst_number",
            "gst_number",
            unique=True,
            postgresql_where="gst_number IS NOT NULL AND deleted_at IS NULL",
        ),
        Index(
            "uq_parties_pan_number",
            "pan_number",
            unique=True,
            postgresql_where="pan_number IS NOT NULL AND deleted_at IS NULL",
        ),
    )
