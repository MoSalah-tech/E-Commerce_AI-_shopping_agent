from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.run import run_agent
from app.core.rate_limit import rate_limit
from app.auth.dependencies import get_current_active_user   # ✅ new JWT dependency
from app.auth.models import User                           # ✅ user model

router = APIRouter()

@router.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[Depends(rate_limit)],      # keep rate limiting
)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),   # ✅ this enforces JWT
) -> ChatResponse:
    result = await run_agent(
        thread_id=request.thread_id,
        user_message=request.message,
    )
    return ChatResponse(**result)