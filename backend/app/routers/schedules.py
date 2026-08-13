from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dog import Dog
from app.models.event import Event
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleOut
from app.services.planner import generate_schedule
from app.services.breed_info import fetch_breed_info, estimate_energy_multiplier

router = APIRouter(prefix="/dogs/{dog_id}/schedule", tags=["schedules"])


def _get_dog_or_404(dog_id: int, db: Session) -> Dog:
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    return dog


@router.get("", response_model=ScheduleOut)
def get_or_generate_schedule(dog_id: int, db: Session = Depends(get_db)):
    _get_dog_or_404(dog_id, db)
    today = date_type.today()

    existing = (
        db.query(Schedule)
        .filter(Schedule.dog_id == dog_id, Schedule.date == today)
        .first()
    )
    if existing:
        return existing

    return _generate_and_save(dog_id, db, today)


@router.post("/regenerate", response_model=ScheduleOut)
def regenerate_schedule(dog_id: int, db: Session = Depends(get_db)):
    _get_dog_or_404(dog_id, db)
    today = date_type.today()

    db.query(Schedule).filter(Schedule.dog_id == dog_id, Schedule.date == today).delete()
    db.commit()

    return _generate_and_save(dog_id, db, today)


def _generate_and_save(dog: Dog, db: Session, today: date_type) -> Schedule:
    events = (
        db.query(Event)
        .filter(Event.dog_id == dog.id)
        .order_by(Event.timestamp.asc())
        .all()
    )

    breed_info = fetch_breed_info(dog.breed or "")
    energy_multiplier = estimate_energy_multiplier(breed_info.temperament)

    generated = generate_schedule(events, energy_multiplier=energy_multiplier)

    schedule = Schedule(
        dog_id=dog.id,
        date=today,
        blocks=[
            {"type": b.type, "time": b.time_str, "reason": b.reason}
            for b in generated.blocks
        ],
        is_adapted=generated.is_adapted,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule