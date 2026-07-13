from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dog_id: int
    date: date
    blocks: list[dict[str, Any]]
    generated_at: datetime
    is_adapted: bool


class PredictionOut(BaseModel):
    last_pee_at: datetime | None
    minutes_since_last_pee: float | None
    predicted_next_pee_at: datetime | None
    probability_needs_out_now: float
    best_moment_in_minutes: float | None
    explanation: str