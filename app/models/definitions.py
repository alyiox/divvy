from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import AuditMixin, Base

# --- CORE IDENTITY ENTITY ---


class User(Base, AuditMixin):
    """
    The User Definition Table (T_User).
    This is the core identity entity for the entire system (Ledger, Groups, Messaging).

    CRITICAL DESIGN CHOICE: Email is set as the primary, unique login identifier.
    The 'username' field serves only as a non-unique display name.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="Unique User ID.")

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="User's unique email address, used as the primary login identifier.",
    )

    username: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="User's preferred display name (not required to be unique)."
    )

    password_hash: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Secured hash of the user's password."
    )

    is_active: Mapped[bool] = mapped_column(
        default=True, comment="Indicates if the user account is active and can participate in new transactions."
    )
