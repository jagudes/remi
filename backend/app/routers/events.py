from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dog import Dog
from app.models.event import Event
from app.schemas.event import EventCreate, EventOut
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dogs/{dog_id}/events", tags=["events"])


def _get_dog_or_404(dog_id: int, user: User, db: Session) -> Dog:
    dog = db.query(Dog).filter(Dog.id == dog_id, Dog.owner_id == user.id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    return dog


@router.post("", response_model=EventOut, status_code=201)
def log_event(dog_id: int, payload: EventCreate, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user),
):
    _get_dog_or_404(dog_id, current_user, db)

    event = Event(
        dog_id=dog_id,
        type=payload.type,
        timestamp=payload.timestamp or datetime.utcnow(),
        metadata_json=payload.metadata or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EventOut])
def list_events(dog_id: int, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    _get_dog_or_404(dog_id,current_user, db)
    return (
        db.query(Event)
        .filter(Event.dog_id == dog_id)
        .order_by(Event.timestamp.desc())
        .limit(limit)
        .all()
    )


@router.delete("/{event_id}", status_code=204)
def delete_event(dog_id: int, event_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user),
):
    _get_dog_or_404(dog_id, current_user, db)
    event = db.query(Event).filter(Event.id == event_id, Event.dog_id == dog_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()