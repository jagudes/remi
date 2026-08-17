from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.dependencies import get_current_user
from app.database import get_db
from app.models.dog import Dog
from app.models.event import Event
from app.schemas.schedule import PredictionOut
from app.services.predictor import predict
from app.services.breed_info import fetch_breed_info, estimate_energy_multiplier
from app.services.age_estimator import estimate_age_multiplier


router = APIRouter(prefix="/dogs/{dog_id}/prediction", tags=["predictions"])


def _get_owned_dog_or_404(dog_id: int, user: User, db: Session) -> Dog:

    dog = db.query(Dog).filter(Dog.id == dog_id, Dog.owner_id == user.id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    return dog

@router.get("", response_model=PredictionOut)
def get_prediction(dog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    dog = _get_owned_dog_or_404(dog_id, current_user, db)

    events = (
        db.query(Event)
        .filter(Event.dog_id == dog_id)
        .order_by(Event.timestamp.asc())
        .all()
    )
    breed_info = fetch_breed_info(dog.breed or "")
    energy_multiplier = estimate_energy_multiplier(breed_info.temperament)
    age_multiplier = estimate_age_multiplier(dog.birth_date)
    combined_multiplier = energy_multiplier * age_multiplier

    result = predict(events, energy_multiplier=combined_multiplier)

    return PredictionOut(
        last_pee_at=result.last_pee_at,
        minutes_since_last_pee=result.minutes_since_last_pee,
        predicted_next_pee_at=result.predicted_next_pee_at,
        probability_needs_out_now=result.probability_needs_out_now,
        best_moment_in_minutes=result.best_moment_in_minutes,
        explanation=result.explanation,
    )