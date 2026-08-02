# app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.run import run_agent
from app.core.rate_limit import rate_limit
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.chat.db import create_thread, thread_belongs_to_user, list_threads

router = APIRouter()

@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(rate_limit)])
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
) -> ChatResponse:

    if not request.thread_id:   # catches both None and ""
        thread_id = await create_thread(current_user.username)
    else:
        owns_thread = await thread_belongs_to_user(request.thread_id, current_user.username)
        if not owns_thread:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Thread not found")
        thread_id = request.thread_id

    result = await run_agent(thread_id=thread_id, user_message=request.message)
    return ChatResponse(thread_id=thread_id, **result)

@router.get("/chat/threads")
async def get_threads(current_user: User = Depends(get_current_active_user)):
    """Lets the frontend build a chat history sidebar later."""
    threads = await list_threads(current_user.username)
    return {"success": True, "data": threads}