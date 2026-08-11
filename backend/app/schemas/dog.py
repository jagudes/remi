from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DogCreate(BaseModel):
    name: str
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    weight_kg: Optional[float] = None


class DogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    breed: Optional[str]
    birth_date: Optional[date]
    weight_kg: Optional[float]

class BreedInfoOut(BaseModel):
    name: str
    temperament: Optional[str]
    bred_for: Optional[str]
    life_span: Optional[str]
    weight_metric: Optional[str]
    breed_group: Optional[str]
    found: bool
    error: Optional[str] = None