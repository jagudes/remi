from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dog import Dog
from app.models.event import Event
from app.schemas.schedule import PredictionOut
from app.services.predictor import predict
from app.services.breed_info import fetch_breed_info, estimate_energy_multiplier


router = APIRouter(prefix="/dogs/{dog_id}/prediction", tags=["predictions"])


@router.get("", response_model=PredictionOut)
def get_prediction(dog_id: int, db: Session = Depends(get_db)):
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

    events = (
        db.query(Event)
        .filter(Event.dog_id == dog_id)
        .order_by(Event.timestamp.asc())
        .all()
    )
    breed_info = fetch_breed_info(dog.breed or "")
    energy_multiplier = estimate_energy_multiplier(breed_info.temperament)

    result = predict(events, energy_multiplier=energy_multiplier)

    return PredictionOut(
        last_pee_at=result.last_pee_at,
        minutes_since_last_pee=result.minutes_since_last_pee,
        predicted_next_pee_at=result.predicted_next_pee_at,
        probability_needs_out_now=result.probability_needs_out_now,
        best_moment_in_minutes=result.best_moment_in_minutes,
        explanation=result.explanation,
    )