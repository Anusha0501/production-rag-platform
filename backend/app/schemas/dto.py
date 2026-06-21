from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentOut(BaseModel):
    id: int
    filename: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    answer: str
    conversation_id: int
    sources: list[str]


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: list[MessageOut] = []

    model_config = {"from_attributes": True}


class EvaluationSummary(BaseModel):
    total_documents: int
    total_conversations: int
    total_messages: int
    retrieval_checks: list[dict[str, str | float]]
