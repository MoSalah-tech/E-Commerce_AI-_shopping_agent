import uuid
from app.core.database import get_pool

async def create_thread(username: str) -> str:
    thread_id = str(uuid.uuid4())
    async with get_pool().connection() as conn:
        await conn.execute(
            "INSERT INTO chat_threads (id, username) VALUES (%s, %s);",
            (thread_id, username),
        )
    return thread_id

async def thread_belongs_to_user(thread_id: str, username: str) -> bool:
    async with get_pool().connection() as conn:
        row = await conn.execute(
            "SELECT 1 FROM chat_threads WHERE id = %s AND username = %s;",
            (thread_id, username),
        )
        return (await row.fetchone()) is not None

async def list_threads(username: str):
    async with get_pool().connection() as conn:
        rows = await conn.execute(
            "SELECT id, title, created_at FROM chat_threads WHERE username = %s ORDER BY created_at DESC;",
            (username,),
        )
        return await rows.fetchall()