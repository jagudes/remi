from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dog import Dog
from app.schemas.dog import DogCreate, DogOut

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