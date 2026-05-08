import uuid
from sqlalchemy import Column, String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ScheduleCache(Base):
    __tablename__ = "schedule_cache"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id     = Column(String, nullable=False)
    entity_type   = Column(String, nullable=False) 
    date = Column(Date, nullable=False)
    data          = Column(JSONB, nullable=False)
    fetched_at    = Column(DateTime, server_default=func.now())