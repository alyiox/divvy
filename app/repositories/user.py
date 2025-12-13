from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.utils import apply_dict_updates
from app.models.definitions import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Retrieves a User by their primary ID."""
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Retrieves a User by their unique email (login ID)."""
        stmt = select(User).where(User.email == email)
        return (await self.session.scalars(stmt)).one_or_none()

    async def create(self, create_data: dict[str, Any]) -> User:
        """Creates a new User record and persists it."""
        sensitive_fields = {"id", "created_at", "created_by"}
        user = User()
        apply_dict_updates(user, create_data, sensitive_fields)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user_id: int, update_data: dict[str, Any]) -> User | None:
        """
        Updates user profile fields using the pure ORM Tracking pattern,
        relying on the utility function and implicit audit hooks.
        """

        user_to_update = await self.get_by_id(user_id)
        if not user_to_update:
            return None

        sensitive_fields = {"id", "password_hash", "created_at", "created_by"}
        apply_dict_updates(entity=user_to_update, update_data=update_data, excluded_attrs=sensitive_fields)

        await self.session.flush()
        await self.session.refresh(user_to_update)

        return user_to_update

    async def update_password(self, user_id: int, new_hashed_password: str) -> None:
        user_to_update = await self.get_by_id(user_id)
        if not user_to_update:
            return None
        user_to_update.password_hash = new_hashed_password
        await self.session.flush()
