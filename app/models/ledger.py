from enum import Enum as PyEnum

from sqlalchemy import DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AuditMixin, Base, TimestampMixin
from .definitions import User


class AccountType(str, PyEnum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    EXPENSE = "Expense"
    INCOME = "Income"
    EQUITY = "Equity"


class AccountSubType(str, PyEnum):
    # Liquid Funds / Cash Accounts
    CASH = "CASH"

    # Debt Tracking (Inter-User)
    AR = "AR"  # Accounts Receivable (others owe me)
    AP = "AP"  # Accounts Payable (I owe others)

    # Debt Tracking (Internal) - Used when a shared transaction is initiated
    PE = "PE"  # Personal Expense (The initial expense recorded by the payer)
    UR = "UR"  # Unsettled Receivables (The liability created for the non-payer)

    # Expense / Consumption Accounts
    SHARED_COST = "SHARED_COST"

    # Settlement/System Accounts
    SETTLEMENT = "SETTLEMENT"  # Used for system-generated balancing/cleanup
    OPENING_EQUITY = "OPENING_EQUITY"  # Replacing 'EQUITY' for clarity on the sub-type


# --- 1. CORE FINANCIAL CONFIGURATION MODELS (Dimensions) ---


class Account(Base, TimestampMixin):
    """
    The Account Classification Definition Table (T_Account).
    Defines all financial accounts (Assets, Liabilities, Expenses, etc.)
    used in the system, serving as the foundational dimension for all bookkeeping.
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="Account Classification ID (e.g., 100-CASH, 200-AP)."
    )
    account_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Account name (e.g., 'Accounts Receivable')."
    )

    account_type: Mapped[AccountType] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="One of the five major accounting elements (Asset, Liability, Expense, etc.).",
    )
    sub_type: Mapped[AccountSubType] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
        comment="Detailed subtype classification (CASH, AR, AP, SHARED_COST, etc.).",
    )


class ExpenseCatalog(Base, AuditMixin):
    """
    The Expense Catalog Table (T_ExpenseCatalog).
    Defines the detailed categories for expenditures, supporting a hierarchical
    (tree) structure for analytical reporting.
    """

    __tablename__ = "expense_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="Expense Catalog ID.")
    catalog_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Name of the expense (e.g., Groceries, Rent, Utilities)."
    )
    parent_id: Mapped[None | int] = mapped_column(
        ForeignKey("expense_catalog.id"), nullable=True, comment="ID of the parent catalog for hierarchy."
    )

    # Relationship definition for hierarchy
    parent = relationship("ExpenseCatalog", remote_side=[id], backref="children")


# --- 2. CORE FINANCIAL FACTS AND STATE MODELS (Facts & State) ---


class AccountEntity(Base, AuditMixin):
    """
    The Account Entity Table (T_AccountEntity).
    Instantiates a financial account for a specific User, serving as the unique
    identifier for balance tracking and ownership.
    """

    __tablename__ = "account_entities"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, comment="Unique Account Entity ID (e.g., User A's CASH account)."
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey(User.id), nullable=False, index=True, comment="The ID of the user who owns this account entity."
    )
    account_type_id: Mapped[int] = mapped_column(
        ForeignKey(Account.id),
        nullable=False,
        index=True,
        comment="The classification ID of this account (links to T_Account).",
    )

    # State field: Cached Balance (must be updated atomically with transactions)
    current_balance: Mapped[float] = mapped_column(
        DECIMAL(14, 4),
        nullable=False,
        default=0.00,
        comment="Cached current balance, derived from aggregating TransactionLogs. Precision is 4 decimal places.",
    )

    # Relationships
    account_type = relationship("Account", backref="entities")
    owner = relationship("User", backref="account_entities")


class TransactionLog(Base, AuditMixin):
    """
    The Transaction Log Table (T_TransactionLog) - The Immutable Ledger.
    The core fact table of the system, recording all debit and credit events.
    All financial reports and balances are derived solely from this table.
    """

    __tablename__ = "transaction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="Unique Log ID.")
    transaction_batch_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="ID linking all entries that must be committed atomically (Debit=Credit).",
    )

    # --- Accounting Balance Fields (Debit = Credit) ---
    debit_account_entity_id: Mapped[int] = mapped_column(
        ForeignKey(AccountEntity.id),
        nullable=False,
        index=True,
        comment="The entity ID receiving the debit (increase in asset/expense, decrease in liability/equity).",
    )
    credit_account_entity_id: Mapped[int] = mapped_column(
        ForeignKey(AccountEntity.id),
        nullable=False,
        index=True,
        comment="The entity ID receiving the credit (increase in liability/equity, decrease in asset/expense).",
    )
    amount: Mapped[float] = mapped_column(
        DECIMAL(14, 4), nullable=False, comment="The transaction amount (must be positive)."
    )

    # --- Business Tracking Fields ---
    counterparty_entity_id: Mapped[None | int] = mapped_column(
        ForeignKey(AccountEntity.id),
        nullable=True,
        index=True,
        comment="The opposing entity ID in AR/AP or PE/UR transactions (used for debt chain tracking).",
    )
    expense_catalog_id: Mapped[None | int] = mapped_column(
        ForeignKey(ExpenseCatalog.id),
        nullable=True,
        index=True,
        comment="Required when a Debit involves an EXPENSE account, specifying the category.",
    )

    narrative: Mapped[None | str] = mapped_column(
        String(255), nullable=True, comment="Detailed description of the transaction."
    )

    # Relationships (ensure foreign_keys are explicitly defined for clarity)
    debit_entity = relationship("AccountEntity", foreign_keys=[debit_account_entity_id], backref="debit_logs")
    credit_entity = relationship("AccountEntity", foreign_keys=[credit_account_entity_id], backref="credit_logs")
    counterparty = relationship("AccountEntity", foreign_keys=[counterparty_entity_id], backref="counterparty_logs")
    expense_catalog_ref = relationship("ExpenseCatalog")
