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

async def set_thread_title_if_missing(thread_id: str, title: str) -> None:
    async with get_pool().connection() as conn:
        await conn.execute(
            "UPDATE chat_threads SET title = %s WHERE id = %s AND title IS NULL;",
            (title[:60], thread_id),
        )



async def delete_thread(thread_id: str, username: str) -> bool:
    """Deletes a thread only if it belongs to this user. Returns True if a row was deleted."""
    async with get_pool().connection() as conn:
        result = await conn.execute(
            "DELETE FROM chat_threads WHERE id = %s AND username = %s;",
            (thread_id, username),
        )
        return result.rowcount > 0