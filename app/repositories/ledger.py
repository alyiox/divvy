from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import TransactionLog


class LedgerRepository:
    """
    Manages data access for the immutable TransactionLog table.
    Focuses on atomic batch recording, auditing, and financial reporting queries.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # --- 1. CORE FACT RECORDING ---

    async def get_next_batch_id(self) -> int:
        """
        Retrieves the next available transaction_batch_id by finding the maximum
        existing ID and incrementing it.
        This is critical for enforcing atomic batches across all logs.
        """
        stmt = select(func.max(TransactionLog.transaction_batch_id))
        max_id = await self.session.scalar(stmt)
        return (max_id or 0) + 1

    async def record_batch(self, logs: list[TransactionLog]) -> int:
        """
        CORE METHOD: Records a list of TransactionLog records atomically under a
        single new batch ID.

        Args:
            logs: A list of pre-validated TransactionLog objects (Debit = Credit check
                  is assumed to have been done in the Service Layer).

        Returns:
            The transaction_batch_id under which the logs were recorded.
        """
        batch_id = await self.get_next_batch_id()

        for log in logs:
            log.transaction_batch_id = batch_id
            self.session.add(log)

        await self.session.flush()
        return batch_id

    # --- 2. AUDIT AND RETRIEVAL ---

    async def get_logs_by_batch_id(self, batch_id: int) -> Sequence[TransactionLog]:
        """
        Retrieves all logs belonging to a specific atomic transaction batch.
        Used for viewing a single transaction (e.g., A paid for B).
        """
        stmt = select(TransactionLog).where(TransactionLog.transaction_batch_id == batch_id)
        return (await self.session.scalars(stmt)).all()

    async def get_logs_for_entity(self, entity_id: int, limit: int = 50) -> Sequence[TransactionLog]:
        """
        Retrieves recent transaction logs where the specified entity was either
        the debit or the credit party.
        """
        stmt = (
            select(TransactionLog)
            .where(
                or_(
                    TransactionLog.debit_account_entity_id == entity_id,
                    TransactionLog.credit_account_entity_id == entity_id,
                )
            )
            .order_by(TransactionLog.id.desc())
            .limit(limit)
        )
        return (await self.session.scalars(stmt)).all()
