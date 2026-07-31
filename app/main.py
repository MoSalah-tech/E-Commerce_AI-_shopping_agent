import sys
import asyncio
from contextlib import asynccontextmanager

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.lifespan import startup, shutdown
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router          # new

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()

app = FastAPI(title="Shopping Agent API", lifespan=lifespan)

app.include_router(health_router)
app.include_router(auth_router)     # new
app.include_router(chat_router)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    print(f"[unhandled_exception_handler] {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "An unexpected server error occurred."},
    )