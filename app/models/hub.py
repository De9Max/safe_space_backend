from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Hub(Base):
    __tablename__ = "hubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model = Column(String)
    api_key = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    last_connection = Column(DateTime(timezone=True))
    ip_address = Column(String)
    space_id = Column(Integer, ForeignKey("spaces.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    space = relationship("Space", back_populates="hubs")
    devices = relationship("Device", back_populates="hub")
