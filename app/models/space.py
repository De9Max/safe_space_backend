from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base
import enum


class SpaceType(enum.Enum):
    HOME = "HOME"
    APARTMENT = "APARTMENT"
    OFFICE = "OFFICE"
    WAREHOUSE = "WAREHOUSE"
    OTHER = "OTHER"


class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(SpaceType), default=SpaceType.HOME)
    address = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="spaces")
    hubs = relationship("Hub", back_populates="space")
    devices = relationship("Device", back_populates="space")
