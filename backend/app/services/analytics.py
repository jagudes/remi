from dataclasses import dataclass
import pandas as pd
from app.models.event import Event, EventType

DEFAULT_MINUTES_AFTER_FOOD = 15
DEFAULT_MINUTES_AFTER_SLEEP = 10
DEFAULT_MINUTES_BETWEEN_PEE = 90
MIN_SAMPLES_FOR_PERSONALIZED_STATS = 3


@dataclass
class BehaviorStats:
    avg_minutes_after_food: float
    avg_minutes_after_sleep: float
    avg_minutes_between_pee: float
    sample_size: int
    is_personalized: bool


def _events_to_dataframe(events: list[Event]) -> pd.DataFrame:
    rows = [
        {
            "type": e.type.value if hasattr(e.type, "value") else e.type,
            "timestamp": pd.Timestamp(e.timestamp),
            "metadata": e.metadata_json or {},
        }
        for e in events
    ]
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def compute_behavior_stats(events: list[Event]) -> BehaviorStats:
    df = _events_to_dataframe(events)

    if df.empty:
        return BehaviorStats(
            avg_minutes_after_food=DEFAULT_MINUTES_AFTER_FOOD,
            avg_minutes_after_sleep=DEFAULT_MINUTES_AFTER_SLEEP,
            avg_minutes_between_pee=DEFAULT_MINUTES_BETWEEN_PEE,
            sample_size=0,
            is_personalized=False,
        )

    pee_times = df[df["type"] == EventType.PEE.value]["timestamp"]

    after_food_gaps = _gaps_after_trigger(df, trigger_type=EventType.FOOD.value)
    after_sleep_gaps = _gaps_after_trigger(df, trigger_type=EventType.SLEEP_END.value)
    between_pee_gaps = pee_times.diff().dt.total_seconds().div(60).dropna()

    sample_size = len(after_food_gaps) + len(after_sleep_gaps) + len(between_pee_gaps)
    personalized = sample_size >= MIN_SAMPLES_FOR_PERSONALIZED_STATS

    return BehaviorStats(
        avg_minutes_after_food=_safe_median(after_food_gaps, DEFAULT_MINUTES_AFTER_FOOD),
        avg_minutes_after_sleep=_safe_median(after_sleep_gaps, DEFAULT_MINUTES_AFTER_SLEEP),
        avg_minutes_between_pee=_safe_median(between_pee_gaps, DEFAULT_MINUTES_BETWEEN_PEE),
        sample_size=sample_size,
        is_personalized=personalized,
    )


def _gaps_after_trigger(df: pd.DataFrame, trigger_type: str) -> pd.Series:
    MAX_WINDOW_MIN = 60
    gaps = []

    triggers = df[df["type"] == trigger_type]
    pees = df[df["type"] == EventType.PEE.value]

    for t_time in triggers["timestamp"]:
        upcoming = pees[pees["timestamp"] > t_time]
        if upcoming.empty:
            continue
        next_pee = upcoming.iloc[0]["timestamp"]
        gap_min = (next_pee - t_time).total_seconds() / 60
        if gap_min <= MAX_WINDOW_MIN:
            gaps.append(gap_min)

    return pd.Series(gaps, dtype="float64")


def _safe_median(series: pd.Series, default: float) -> float:
    if series.empty:
        return default
    return float(series.median())


def count_recent_accidents(events: list[Event], lookback: int = 20) -> int:
    df = _events_to_dataframe(events)
    if df.empty:
        return 0

    pees = df[df["type"] == EventType.PEE.value].tail(lookback)
    accidents = pees["metadata"].apply(lambda m: m.get("location") == "inside")
    return int(accidents.sum())