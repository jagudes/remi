from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Schedule(Base):

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"), nullable=False)

    date = Column(Date, nullable=False)
    blocks = Column(JSON, nullable=False, default=list)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_adapted = Column(Boolean, default=False)  # czy plan przebudowany po wypadkach

    dog = relationship("Dog", back_populates="schedules")