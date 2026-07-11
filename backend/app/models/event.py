import enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class EventType(str, enum.Enum):
    PEE = "pee"
    POOP = "poop"
    FOOD = "food"
    SLEEP_START = "sleep_start"
    SLEEP_END = "sleep_end"
    WALK = "walk"


class Event(Base):

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)

    type = Column(Enum(EventType), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metadata_json = Column(JSON, nullable=True, default=dict)

    dog = relationship("Dog", back_populates="events")