from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.models import Conversation, Document, Message, User
from app.repositories.unit_of_work import Repository
from app.schemas.dto import ChatRequest, ChatResponse, ConversationOut, DocumentOut, EvaluationSummary, Token, UserCreate
from app.services.rag import RagService, persist_upload

router = APIRouter(prefix="/api")


@router.post("/auth/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    repo = Repository(db)
    if repo.user_by_email(payload.email):
        raise HTTPException(409, "Email already registered")
    repo.add(User(email=payload.email, hashed_password=hash_password(payload.password)))
    return Token(access_token=create_access_token(payload.email))


@router.post("/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = Repository(db).user_by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return Token(access_token=create_access_token(user.email))


@router.post("/documents", response_model=DocumentOut)
def upload_document(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF uploads are supported")
    path = persist_upload(file.filename or "document.pdf", file.file.read())
    collection, _ = RagService().ingest_pdf(user.id, path)
    return Repository(db).add(Document(owner_id=user.id, filename=file.filename or "document.pdf", chroma_collection=collection))


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return Repository(db).documents_for_user(user.id)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    repo = Repository(db)
    conversation = repo.conversation_for_user(payload.conversation_id, user.id) if payload.conversation_id else None
    if conversation is None:
        conversation = repo.add(Conversation(user_id=user.id, title=payload.question[:80]))
    answer, sources = RagService().answer(user.id, payload.question)
    db.add_all([
        Message(conversation_id=conversation.id, role="user", content=payload.question),
        Message(conversation_id=conversation.id, role="assistant", content=answer),
    ])
    db.commit()
    return ChatResponse(answer=answer, conversation_id=conversation.id, sources=sources)


@router.get("/conversations", response_model=list[ConversationOut])
def conversations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return Repository(db).conversations_for_user(user.id)


@router.get("/evaluations", response_model=EvaluationSummary)
def evaluations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    repo = Repository(db)
    docs = repo.documents_for_user(user.id)
    checks = [{"name": "document_ingestion", "score": 1.0 if docs else 0.0, "status": "ready" if docs else "needs_data"}]
    return EvaluationSummary(
        total_documents=len(docs),
        total_conversations=len(repo.conversations_for_user(user.id)),
        total_messages=repo.message_count_for_user(user.id),
        retrieval_checks=checks,
    )
