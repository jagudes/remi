from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Dog(Base):
    __tablename__ = "dogs"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    breed = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    weight_kg = Column(Float, nullable=True)

    owner = relationship("User", back_populates="dogs")
    events = relationship("Event", back_populates="dog", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="dog", cascade="all, delete-orphan")