from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime

from app.models.device import DeviceType

if TYPE_CHECKING:
    from app.schemas.event import EventOut


class DeviceBase(BaseModel):
    name: str
    type: DeviceType
    zigbee_id: Optional[str] = None
    location: Optional[str] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DeviceCreate(DeviceBase):
    hub_id: Optional[int] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    hub_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class DeviceInDB(DeviceBase):
    id: int
    is_active: bool
    battery_level: Optional[float] = None
    last_seen: Optional[datetime] = None
    hub_id: Optional[int] = None
    space_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class DeviceOut(DeviceInDB):
    pass


class DeviceWithEventsOut(DeviceOut):
    events: List["EventOut"] = []
