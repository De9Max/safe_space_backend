from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base
import enum


class EventType(enum.Enum):
    MOTION_DETECTED = "motion_detected"
    DOOR_OPENED = "door_opened"
    WINDOW_OPENED = "window_opened"
    SMOKE_DETECTED = "smoke_detected"
    WATER_LEAK_DETECTED = "water_leak_detected"
    TEMPERATURE = 'temperature'
    BATTERY = 'battery'
    HUMIDITY = "humidity"
    POOR_AIR_QUALITY = "poor_air_quality"
    DEVICE_OFFLINE = "device_offline"
    DEVICE_ONLINE = "device_online"
    OTHER = "other"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(EventType), nullable=False)
    data = Column(JSON)
    processed = Column(Boolean, default=False)
    device_id = Column(Integer, ForeignKey("devices.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("Device", back_populates="events")
    incident = relationship("Incident", back_populates="event", uselist=False)
