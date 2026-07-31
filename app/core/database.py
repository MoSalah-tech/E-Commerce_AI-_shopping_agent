from typing import Optional
from psycopg_pool import AsyncConnectionPool
from app.core.config import postgres_url
import psycopg.rows

_pool: Optional[AsyncConnectionPool] = None

async def init_pool():
    global _pool
    _pool = AsyncConnectionPool(
        conninfo=postgres_url,
        max_size=20,
        kwargs={"autocommit": True, "prepare_threshold": 0 , "row_factory":psycopg.rows.dict_row},
    )
    await _pool.open()
    # Table creation is handled manually – uncomment if you want the app to auto-create:
    # await _create_users_table()

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

def get_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialised. Call init_pool() first.")
    return _pool