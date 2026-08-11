from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dog import Dog
from app.schemas.dog import DogCreate, DogOut, BreedInfoOut
from app.services.breed_info import fetch_breed_info

router = APIRouter(prefix="/dogs", tags=["dogs"])

DEFAULT_OWNER_ID = 1


@router.post("", response_model=DogOut, status_code=201)
def create_dog(payload: DogCreate, db: Session = Depends(get_db)):
    dog = Dog(owner_id=DEFAULT_OWNER_ID, **payload.model_dump())
    db.add(dog)
    db.commit()
    db.refresh(dog)
    return dog


@router.get("", response_model=list[DogOut])
def list_dogs(db: Session = Depends(get_db)):
    return db.query(Dog).filter(Dog.owner_id == DEFAULT_OWNER_ID).all()


@router.get("/{dog_id}", response_model=DogOut)
def get_dog(dog_id: int, db: Session = Depends(get_db)):
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    return dog


@router.delete("/{dog_id}", status_code=204)
def delete_dog(dog_id: int, db: Session = Depends(get_db)):
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    db.delete(dog)
    db.commit()

@router.get("/{dog_id}/breed-info", response_model=BreedInfoOut)
def get_breed_info(dog_id: int, db: Session = Depends(get_db)):
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

    info = fetch_breed_info(dog.breed or "")

    return BreedInfoOut(
        name=info.name,
        temperament=info.temperament,
        bred_for=info.bred_for,
        life_span=info.life_span,
        weight_metric=info.weight_metric,
        breed_group=info.breed_group,
        found=info.found,
        error=info.error,
    )