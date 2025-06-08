from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime


class HubBase(BaseModel):
    name: str
    model: Optional[str] = None


class HubCreate(HubBase):
    pass


class HubUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    is_active: Optional[bool] = None


class HubInDB(HubBase):
    id: int
    api_key: str
    is_active: bool
    space_id: int
    last_connection: Optional[datetime] = None
    ip_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class HubOut(HubInDB):
    device_count: int = 0
