import uuid
from sqlalchemy import Column, String, func, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    subject = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    compiled_at = Column(DateTime(timezone=True), nullable=True)
    md_content = Column(Text, nullable=True)


class Fragment(Base):
    __tablename__ = "fragments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    index  = Column(Integer, nullable=False)
    markdown_text = Column(Text, nullable=False)
    gigachat_file_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
