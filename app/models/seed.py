from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .ledger import Account, AccountSubType, AccountType, ExpenseCatalog

# --- STATIC DATA DEFINITIONS ---

# 1. T_Account Seed Data: These are mandatory for the double-entry system
# Structure: (account_name, AccountType, AccountSubType, id)
ACCOUNTS_SEED_DATA: list[tuple[str, AccountType, AccountSubType, int]] = [
    # ASSETS (1xx)
    ("Cash & Bank Accounts", AccountType.ASSET, AccountSubType.CASH, 100),
    ("Accounts Receivable", AccountType.ASSET, AccountSubType.AR, 110),
    ("Prepaid Expenses", AccountType.ASSET, AccountSubType.PE, 120),
    # LIABILITIES (2xx)
    ("Accounts Payable", AccountType.LIABILITY, AccountSubType.AP, 210),
    ("Unearned Revenue", AccountType.LIABILITY, AccountSubType.UR, 220),
    ("System Settlement Liability", AccountType.LIABILITY, AccountSubType.SETTLEMENT, 230),
    # EQUITY (3xx)
    ("Owner's Equity (Starting Balance)", AccountType.EQUITY, AccountSubType.OPENING_EQUITY, 300),
    # EXPENSE (4xx)
    ("General Shared Costs", AccountType.EXPENSE, AccountSubType.SHARED_COST, 400),
    # INCOME (5xx)
    ("Service/External Income", AccountType.INCOME, AccountSubType.SETTLEMENT, 500),
]


# 2. T_ExpenseCatalog Seed Data: Base categories for spending analysis
# Structure: (catalog_name, parent_name_or_None)
CATALOG_SEED_DATA: list[tuple[str, str | None]] = [
    # Top Level Categories
    ("Living Expenses", None),
    ("Entertainment", None),
    ("Utilities", None),
    ("Debt Repayments", None),
    # Sub-Categories
    ("  - Groceries", "Living Expenses"),
    ("  - Rent", "Living Expenses"),
    ("  - Transportation", "Living Expenses"),
    ("  - Streaming Services", "Entertainment"),
    ("  - Dining Out", "Entertainment"),
    ("  - Electricity Bill", "Utilities"),
    ("  - Water Bill", "Utilities"),
]

# --- SEEDING FUNCTIONS ---


def initialize_accounts(session: Session) -> dict[AccountSubType, Account]:
    """
    Initializes the T_Account table with all required core financial classifications.
    Uses hardcoded IDs for consistency across environments.
    """
    print("--- Initializing T_Account Classifications ---")
    account_map: dict[AccountSubType, Account] = {}

    for name, acc_type, sub_type, id_hint in ACCOUNTS_SEED_DATA:
        # Check if the account already exists by sub_type
        existing_account = session.query(Account).filter_by(sub_type=sub_type).first()

        if existing_account:
            print(f"  [Skipped] Account {sub_type} already exists.")
            account_map[sub_type] = existing_account
            continue

        new_account = Account(id=id_hint, account_name=name, account_type=acc_type, sub_type=sub_type)
        session.add(new_account)
        account_map[sub_type] = new_account
        print(f"  [Created] ID {id_hint}: {name} ({sub_type})")

    # Commit after creating all accounts
    session.commit()
    return account_map


def initialize_expense_catalogs(session: Session):
    """
    Initializes the T_ExpenseCatalog table, handling the parent-child hierarchy.
    This process requires two passes: 1) Create all parents, 2) Create all children
    and assign FKs.
    """
    print("\n--- Initializing T_ExpenseCatalog Categories ---")
    catalog_map: dict[str, ExpenseCatalog] = {}

    # Pass 1: Create all top-level parents first
    for name, parent_name in CATALOG_SEED_DATA:
        cleaned_name = name.strip(" -")

        if parent_name is None:
            # Only create if it doesn't exist
            existing_catalog = (
                session.query(ExpenseCatalog).filter_by(catalog_name=cleaned_name, parent_id=None).first()
            )
            if not existing_catalog:
                new_catalog = ExpenseCatalog(catalog_name=cleaned_name)
                session.add(new_catalog)
                catalog_map[cleaned_name] = new_catalog
                print(f"  [Created Parent] {cleaned_name}")
            else:
                catalog_map[cleaned_name] = existing_catalog

    session.flush()  # Ensure parent IDs are available before creating children

    # Pass 2: Create sub-categories and link them using parent_id
    for name, parent_name in CATALOG_SEED_DATA:
        cleaned_name = name.strip(" -")

        if parent_name is not None:
            parent_catalog = (
                catalog_map.get(parent_name)
                or session.query(ExpenseCatalog).filter_by(catalog_name=parent_name, parent_id=None).first()
            )

            if parent_catalog:
                # Check for existing child (to prevent duplicates)
                existing_child = (
                    session.query(ExpenseCatalog)
                    .filter_by(catalog_name=cleaned_name, parent_id=parent_catalog.id)
                    .first()
                )

                if not existing_child:
                    new_catalog = ExpenseCatalog(catalog_name=cleaned_name, parent_id=parent_catalog.id)
                    session.add(new_catalog)
                    print(f"  [Created Child] {cleaned_name} (Parent: {parent_name})")
            else:
                print(f"  [Warning] Could not find parent catalog: {parent_name}")

    session.commit()


# Optional: Function to create test users and initial entities (e.g., A_CASH, B_CASH)
# and potentially a sample TransactionLog for demonstration, but omitted here for brevity.


def run_seeding(session: Session):
    """
    The main entry point to execute all seeding functions.
    """
    print("\n--- STARTING DATABASE SEEDING PROCESS ---")
    try:
        initialize_accounts(session)
        initialize_expense_catalogs(session)
        print("\n✅ All core configuration data has been successfully seeded.")
    except IntegrityError:
        session.rollback()
        print("\n❌ Seeding failed due to Integrity Error (e.g., duplicate IDs/names). Transaction rolled back.")
    except Exception as e:
        session.rollback()
        print(f"\n❌ An unexpected error occurred during seeding. Transaction rolled back. Error: {e}")


# Note: In a real application, you would connect to the DB and pass the session object to run_seeding().
