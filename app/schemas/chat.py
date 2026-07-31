from typing import Any, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    thread_id: str
    message: str


class ChatResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None



class HealthResponse(BaseModel):
    status: str