from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.password import check_password, hash_password
from app.exceptions.http import ValidationError
from app.models.definitions import User
from app.repositories import AccountRepository, UserRepository
from app.schemas import LoginRequest, PasswordChangeRequest, ProfileRequest, UserRequest, UserResponse


class UserService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository, account_repo: AccountRepository):
        self._session = session
        self._user_repo = user_repo
        self._account_repo = account_repo

    # --- 1. USER REGISTRATION (Atomic Operation) ---

    async def register_user(self, data: UserRequest, initial_cash_balance: Decimal = Decimal("0.0")) -> UserResponse:
        """
        Registers a new user ATOMICALLY: creating identity, mandatory accounts,
        and the opening balance transaction.
        """

        if not data.password:
            raise ValidationError("Password is required for user registration.")

        if await self._user_repo.get_by_email(data.email):
            raise ValidationError("User with this email already exists.")

        hashed_password = hash_password(data.password)

        # --- START ATOMIC TRANSACTION ---
        async with self._session.begin():

            new_user_data = data.model_dump(exclude={"password"})
            new_user_data["password_hash"] = hashed_password
            created_user: User = await self._user_repo.create(new_user_data)

            await self._account_repo.create_initial_entities(created_user.id)

            ## 3. Handle Initial Cash Balance (If > 0)
            # if initial_cash_balance > Decimal("0.0"):
            #    # This must be the final step in the atomic boundary.
            #    cash_entity_id = await self._account_repo.get_entity_id(created_user.id, AccountSubType.CASH)
            #    equity_entity_id = await self._account_repo.get_entity_id(
            #        created_user.id, AccountSubType.OPENING_EQUITY
            #    )

            #    await self.ledger_service.post_opening_balance(cash_entity_id, equity_entity_id, initial_cash_balance)

            # --- END ATOMIC TRANSACTION ---

            return UserResponse.model_validate(created_user)

    # --- 2. USER AUTHENTICATION ---

    async def authenticate(self, credentials: LoginRequest) -> UserResponse | None:
        """
        Authenticates a user by email and password using secure hashing.
        """
        # 1. Retrieve the user record, including the stored hash
        user_orm = await self._user_repo.get_by_email(credentials.email)

        if not user_orm or not user_orm.is_active:
            return None

        # 2. Perform cryptographic verification
        if check_password(credentials.password, user_orm.password_hash):
            # 3. Success: Return the user data mapped to the response schema
            return UserResponse.model_validate(user_orm)

        return None

    # --- 3. PASSWORD AND PROFILE MANAGEMENT ---

    async def update_profile(self, user_id: int, actor_id: int, data: ProfileRequest) -> UserResponse | None:
        """
        Updates non-password related user profile fields.
        """
        # Note: This is a simpler update; no need for an atomic transaction boundary unless
        # it involves other linked entities (which it currently does not).

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            user_orm = await self._user_repo.get_by_id(user_id)  # Return current if nothing to update
            return UserResponse.model_validate(user_orm) if user_orm else None

        updated_user_orm = await self._user_repo.update(user_id, update_data)

        if updated_user_orm:
            return UserResponse.model_validate(updated_user_orm)
        return None

    async def change_password(self, user_id: int, actor_id: int, data: PasswordChangeRequest) -> bool:
        """
        Changes the user's password after verifying the old password.
        """
        user_orm = await self._user_repo.get_by_id(user_id)

        if not user_orm:
            return False

        if not check_password(data.old_password, user_orm.password_hash):
            return False

        new_password_hash = hash_password(data.new_password)

        await self._user_repo.update_password(user_id, new_password_hash)

        return True
