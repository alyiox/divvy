from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import Account, AccountEntity, AccountSubType, ExpenseCatalog


class AccountRepository:
    """
    Manages data access for financial configuration (Account, ExpenseCatalog)
    and the user-specific state model (AccountEntity).
    """

    # Policy: The five essential accounts every user must start with
    _REQUIRED_SUB_TYPES = [
        AccountSubType.CASH,
        AccountSubType.AR,
        AccountSubType.AP,
        AccountSubType.OPENING_EQUITY,
        AccountSubType.SHARED_COST,
    ]

    def __init__(self, session: AsyncSession):
        self.session = session

    # --- 1. Account Entity (State) Methods ---

    async def get_entity_by_id(self, entity_id: int) -> AccountEntity | None:
        """Retrieves an AccountEntity by its ID."""
        return await self.session.get(AccountEntity, entity_id)

    async def get_user_entities(self, user_id: int) -> Sequence[AccountEntity]:
        """
        Retrieves all AccountEntity records owned by a specific user.
        Used to build a user's personal balance sheet.
        """
        stmt = select(AccountEntity).where(AccountEntity.owner_id == user_id).order_by(AccountEntity.account_type_id)
        return (await self.session.scalars(stmt)).all()

    async def create_initial_entities(self, user_id: int) -> None:
        """
        Creates the set of mandatory AccountEntity records for a new user based
        on the internal REQUIRED_SUB_TYPES policy. Queries the database for static IDs.
        """

        # 1. Query the database to get the static IDs (Source of Truth)
        # This is the single, simple, runtime query.
        account_ids_map = await self._fetch_account_ids_by_sub_types(self._REQUIRED_SUB_TYPES)

        entities_to_create: list[AccountEntity] = []

        # 2. Prepare AccountEntity instances
        for sub_type in self._REQUIRED_SUB_TYPES:
            account_id = account_ids_map.get(sub_type)
            if not account_id:
                raise RuntimeError(f"Static ID for {sub_type.value} not found in database. Check seed data.")

            entity = AccountEntity(owner_user_id=user_id, account_id=account_id, current_balance=0.00)
            entities_to_create.append(entity)

        # 3. Add to Session (Relies on caller's transaction boundary)
        self.session.add_all(entities_to_create)
        await self.session.flush()

    async def _fetch_account_ids_by_sub_types(self, sub_types: list[AccountSubType]) -> dict[AccountSubType, int]:
        """
        Retrieves the static database IDs for a list of Account SubTypes.
        This hits the database on every call to ensure the latest data is used.
        """
        sub_type_strings = [st.value for st in sub_types]

        stmt = select(Account.id, Account.sub_type).where(Account.sub_type.in_(sub_type_strings))
        result = await self.session.execute(stmt)

        # Map the results back from (id, 'sub_type_string') to {AccountSubType.ENUM: id}
        return {AccountSubType(sub_type_str): id for id, sub_type_str in result.all()}

    async def update_balance_cache(self, entity_id: int, amount_delta: float) -> AccountEntity:
        """
        CRITICAL: Atomically updates the current_balance cache for a specific AccountEntity.
        This must be called immediately after a TransactionLog batch is successfully committed.

        Args:
            entity_id: The ID of the AccountEntity to update.
            amount_delta: The change in balance (positive for increase, negative for decrease).

        Raises:
            NoResultFound: If the entity ID does not exist.
        """
        # SQLAlchemy 2.0 style UPDATE statement for efficiency and atomicity
        stmt = (
            update(AccountEntity)
            .where(AccountEntity.id == entity_id)
            .values(current_balance=AccountEntity.current_balance + amount_delta)
            .returning(AccountEntity)  # Return the updated object
        )

        result = await self.session.execute(stmt)
        updated_entity = result.scalar_one_or_none()

        if not updated_entity:
            raise NoResultFound(f"AccountEntity with ID {entity_id} not found for balance update.")

        return updated_entity

    # --- 2. Account (Configuration) Methods ---

    async def get_account_by_sub_type(self, sub_type: AccountSubType) -> Account:
        """
        Retrieves a static Account classification by its unique sub_type (e.g., 'CASH').
        Raises NoResultFound if the type is not found (database not seeded correctly).
        """
        stmt = select(Account).where(Account.sub_type == sub_type)
        return (await self.session.scalars(stmt)).one()

    # --- 3. Expense Catalog (Configuration) Methods ---

    async def get_expense_catalog_by_id(self, catalog_id: int) -> ExpenseCatalog | None:
        """Retrieves an ExpenseCatalog by ID."""
        return await self.session.get(ExpenseCatalog, catalog_id)

    async def get_expense_catalog_by_name(self, name: str) -> ExpenseCatalog | None:
        """Retrieves an ExpenseCatalog by name."""
        stmt = select(ExpenseCatalog).where(ExpenseCatalog.catalog_name == name)
        return (await self.session.scalars(stmt)).one_or_none()
