from pydantic import BaseModel, Field
from typing import Optional

class AnalyzeRequest(BaseModel):
    code: str
    filename: str
    language: Optional[str] = None
    github_url: Optional[str] = None

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    code: str
    filename: str
    language: Optional[str] = None
    chat_history: list[dict] = []

class AnalyzeResponse(BaseModel):
    summary: str
    language: str
    filename: str
    line_count: int

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []

class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
