from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base
import enum


class DeviceType(enum.Enum):
    CAMERA = "camera"
    MOTION_SENSOR = "motion_sensor"
    DOOR_SENSOR = "door_sensor"
    WINDOW_SENSOR = "window_sensor"
    SMOKE_DETECTOR = "smoke_detector"
    WATER_LEAK_SENSOR = "water_leak_sensor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    AIR_QUALITY_SENSOR = "air_quality_sensor"
    OTHER = "other"


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(DeviceType), nullable=False)
    zigbee_id = Column(String, unique=True, index=True)
    location = Column(String)
    is_active = Column(Boolean, default=True)
    battery_level = Column(Float)
    config = Column(JSON)
    last_seen = Column(DateTime(timezone=True))
    hub_id = Column(Integer, ForeignKey("hubs.id"))
    space_id = Column(Integer, ForeignKey("spaces.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hub = relationship("Hub", back_populates="devices")
    space = relationship("Space", back_populates="devices")
    events = relationship("Event", back_populates="device")
