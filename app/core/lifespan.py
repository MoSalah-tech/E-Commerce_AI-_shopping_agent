from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.database import init_pool, close_pool, get_pool
from app.agent.graph import workflow

_graph = None

def get_graph():
    if _graph is None:
        raise RuntimeError("Agent graph is not initialized. Call startup() first.")
    return _graph

async def startup():
    global _graph

    await init_pool()

    pool = get_pool()
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()

    _graph = workflow.compile(checkpointer=checkpointer)

async def shutdown():
    await close_pool()