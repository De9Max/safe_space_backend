from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.event import EventType


class EventBase(BaseModel):
    type: EventType
    data: Optional[Dict[str, Any]] = None


class EventCreate(EventBase):
    device_id: Optional[int] = None
    zigbee_id: Optional[str] = None  # Для ідентифікації пристрою за Zigbee ID

    @validator('device_id', 'zigbee_id')
    def validate_identifiers(cls, v, values, **kwargs):
        if 'device_id' in values and values['device_id'] is None and 'zigbee_id' in values and values[
            'zigbee_id'] is None:
            raise ValueError('Either device_id or zigbee_id must be provided')
        return v


class EventInDB(EventBase):
    id: int
    device_id: int
    processed: bool
    created_at: datetime

    class Config:
        orm_mode = True


class EventOut(EventInDB):
    pass
