from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.routers import dogs, events

app = FastAPI(title="Remi API")

app.include_router(dogs.router)
app.include_router(events.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    _seed_default_user()


def _seed_default_user():
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.id == 1).first()
        if not existing:
            user = User(email="test@remi.dev", password_hash="not-used-yet")
            db.add(user)
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}