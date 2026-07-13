from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict

from app.models.event import EventType


class EventCreate(BaseModel):
    type: EventType
    timestamp: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dog_id: int
    type: EventType
    timestamp: datetime
    metadata_json: Optional[dict[str, Any]] = None