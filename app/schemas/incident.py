from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.incident import IncidentStatus, IncidentSeverity
from app.schemas.event import EventOut


class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    data: Optional[Dict[str, Any]] = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentInDB(IncidentBase):
    id: int
    status: IncidentStatus
    event_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class IncidentOut(IncidentInDB):
    pass


class IncidentWithEventOut(IncidentOut):
    event: EventOut

    class Config:
        orm_mode = True
