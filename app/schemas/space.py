from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.space import SpaceType


class SpaceBase(BaseModel):
    name: str
    type: SpaceType = SpaceType.HOME
    address: Optional[str] = None


class SpaceCreate(SpaceBase):
    pass


class SpaceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[SpaceType] = None
    address: Optional[str] = None


class SpaceInDB(SpaceBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SpaceOut(SpaceInDB):
    device_count: int = 0
    hub_count: int = 0
