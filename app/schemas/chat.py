from typing import Any, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    success: bool
    thread_id: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None



class HealthResponse(BaseModel):
    status: str