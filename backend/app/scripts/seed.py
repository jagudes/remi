import random
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.event import Event, EventType

DOG_ID = 7
DAYS_TO_GENERATE = 20


def generate_day_events(day_start: datetime) -> list[Event]:
    events = []
    current_time = day_start

    events.append(Event(dog_id=DOG_ID, type=EventType.SLEEP_END, timestamp=current_time))

    for meal_num in range(4):
        meal_time = current_time + timedelta(minutes=random.randint(0, 20))
        events.append(Event(dog_id=DOG_ID, type=EventType.FOOD, timestamp=meal_time))

        pee_delay = max(5, int(random.gauss(15, 4)))
        pee_time = meal_time + timedelta(minutes=pee_delay)
        location = "inside" if random.random() < 0.10 else "outside"
        events.append(
            Event(
                dog_id=DOG_ID,
                type=EventType.PEE,
                timestamp=pee_time,
                metadata_json={"location": location, "after": "food"},
            )
        )

        nap_start = pee_time + timedelta(minutes=random.randint(20, 40))
        events.append(Event(dog_id=DOG_ID, type=EventType.SLEEP_START, timestamp=nap_start))

        nap_length = random.randint(60, 100)
        nap_end = nap_start + timedelta(minutes=nap_length)
        events.append(Event(dog_id=DOG_ID, type=EventType.SLEEP_END, timestamp=nap_end))

        wake_pee_delay = max(3, int(random.gauss(10, 3)))
        wake_pee_time = nap_end + timedelta(minutes=wake_pee_delay)
        location = "inside" if random.random() < 0.10 else "outside"
        events.append(
            Event(
                dog_id=DOG_ID,
                type=EventType.PEE,
                timestamp=wake_pee_time,
                metadata_json={"location": location, "after": "sleep"},
            )
        )

        current_time = wake_pee_time + timedelta(minutes=random.randint(30, 60))

    return events


def main():
    db = SessionLocal()
    try:
        today = datetime.now(timezone.utc).date()
        all_events = []

        for days_ago in range(DAYS_TO_GENERATE, 0, -1):
            day_date = today - timedelta(days=days_ago)
            day_start = datetime.combine(
                day_date, datetime.min.time(), tzinfo=timezone.utc
            ) + timedelta(hours=7)
            all_events.extend(generate_day_events(day_start))

        db.add_all(all_events)
        db.commit()
        print(f"Dodano {len(all_events)} zdarzeń dla psa o id={DOG_ID} ({DAYS_TO_GENERATE} dni historii).")
    finally:
        db.close()


if __name__ == "__main__":
    main()