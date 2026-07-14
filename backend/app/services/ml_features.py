import pandas as pd

from app.models.event import Event, EventType

MAX_WINDOW_MIN = 180
TRIGGER_TYPES = [EventType.FOOD.value, EventType.SLEEP_END.value, EventType.PEE.value]


def build_training_table(events: list[Event]) -> pd.DataFrame:
    rows = [
        {
            "type": e.type.value if hasattr(e.type, "value") else e.type,
            "timestamp": pd.Timestamp(e.timestamp),
        }
        for e in events
    ]
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=["trigger_type", "hour_of_day", "minutes_since_prev_pee", "gap_to_next_pee_minutes"]
        )

    df = df.sort_values("timestamp").reset_index(drop=True)
    pee_times = df[df["type"] == EventType.PEE.value]["timestamp"].tolist()

    training_rows = []

    for trigger_type in TRIGGER_TYPES:
        triggers = df[df["type"] == trigger_type]

        for t_time in triggers["timestamp"]:
            upcoming_pees = [p for p in pee_times if p > t_time]
            if not upcoming_pees:
                continue
            next_pee = min(upcoming_pees)
            gap_min = (next_pee - t_time).total_seconds() / 60
            if gap_min <= 0 or gap_min > MAX_WINDOW_MIN:
                continue

            previous_pees = [p for p in pee_times if p <= t_time]
            minutes_since_prev_pee = (
                (t_time - max(previous_pees)).total_seconds() / 60
                if previous_pees
                else MAX_WINDOW_MIN  # brak wcześniejszego siku - traktujemy jako "dawno"
            )

            training_rows.append(
                {
                    "trigger_type": trigger_type,
                    "hour_of_day": t_time.hour,
                    "minutes_since_prev_pee": minutes_since_prev_pee,
                    "gap_to_next_pee_minutes": gap_min,
                }
            )

    return pd.DataFrame(training_rows)