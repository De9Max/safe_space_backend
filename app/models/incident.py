from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base
import enum


class IncidentStatus(enum.Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class IncidentSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.NEW)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    data = Column(JSON)
    event_id = Column(Integer, ForeignKey("events.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))

    event = relationship("Event", back_populates="incident")
