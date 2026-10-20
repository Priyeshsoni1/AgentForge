
from psycopg_pool import AsyncConnectionPool


class ConversationStore:
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool

    async def setup(self) -> None:
        async with self.pool.connection() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_conversations (
                    thread_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

    async def claim_or_verify(
        self,
        thread_id: str,
        owner_id: str,
    ) -> None:
        async with self.pool.connection() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO agent_conversations (thread_id, owner_id)
                    VALUES (%s, %s)
                    ON CONFLICT (thread_id) DO NOTHING
                    """,
                    (thread_id, owner_id),
                )

                cursor = await conn.execute(
                    """
                    SELECT owner_id
                    FROM agent_conversations
                    WHERE thread_id = %s
                    """,
                    (thread_id,),
                )
                row = await cursor.fetchone()

                if row is None or row[0] != owner_id:
                    raise PermissionError(
                        "Conversation does not belong to this API-key owner."
                    )
