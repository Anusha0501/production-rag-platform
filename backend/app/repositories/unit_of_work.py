from sqlalchemy.orm import Session
from app.domain.models import Conversation, Document, Message, User


class Repository:
    def __init__(self, db: Session):
        self.db = db

    def user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def add(self, obj):
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def documents_for_user(self, user_id: int) -> list[Document]:
        return self.db.query(Document).filter(Document.owner_id == user_id).order_by(Document.created_at.desc()).all()

    def conversations_for_user(self, user_id: int) -> list[Conversation]:
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at.desc()).all()

    def conversation_for_user(self, conversation_id: int, user_id: int) -> Conversation | None:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()

    def count_for_user(self, model, user_id_field, user_id: int) -> int:
        return self.db.query(model).filter(user_id_field == user_id).count()

    def message_count_for_user(self, user_id: int) -> int:
        return self.db.query(Message).join(Conversation).filter(Conversation.user_id == user_id).count()
