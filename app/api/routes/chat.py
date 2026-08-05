# app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.run import run_agent
from app.core.rate_limit import rate_limit
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.chat.db import (
    create_thread,
    thread_belongs_to_user,
    list_threads,
    set_thread_title_if_missing,
    delete_thread,
    )
from app.core.lifespan import get_graph
router = APIRouter()

@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(rate_limit)])
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
) -> ChatResponse:

    if not request.thread_id:
        thread_id = await create_thread(current_user.username)
    else:
        owns_thread = await thread_belongs_to_user(request.thread_id, current_user.username)
        if not owns_thread:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Thread not found")
        thread_id = request.thread_id

    result = await run_agent(thread_id=thread_id, user_message=request.message)

    if result.get("success"):
        await set_thread_title_if_missing(thread_id, request.message)

    return ChatResponse(thread_id=thread_id, **result)


@router.get("/chat/threads")
async def get_threads(current_user: User = Depends(get_current_active_user)):
    threads = await list_threads(current_user.username)
    return {"success": True, "data": threads}


@router.get("/chat/threads/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Returns the chat_history LangGraph has checkpointed for this thread,
    so the frontend can render a previous conversation when it's selected."""
    owns_thread = await thread_belongs_to_user(thread_id, current_user.username)
    if not owns_thread:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Thread not found")

    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.aget_state(config)
    chat_history = state.values.get("chat_history", []) if state else []

    return {"success": True, "data": chat_history}



@router.delete("/chat/threads/{thread_id}")
async def delete_chat_thread(
    thread_id: str,
    current_user: User = Depends(get_current_active_user),
):
    deleted = await delete_thread(thread_id, current_user.username)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    return {"success": True, "message": "Thread deleted"}