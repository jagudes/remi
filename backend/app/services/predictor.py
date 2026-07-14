from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.models.event import Event, EventType
from app.services.analytics import BehaviorStats, compute_behavior_stats


@dataclass
class Prediction:
    last_pee_at: datetime | None
    minutes_since_last_pee: float | None
    predicted_next_pee_at: datetime | None
    probability_needs_out_now: float
    best_moment_in_minutes: float | None
    explanation: str


def _last_event_of_type(events: list[Event], event_type: EventType) -> Event | None:
    matching = [e for e in events if e.type == event_type]
    if not matching:
        return None
    return max(matching, key=lambda e: e.timestamp)


def predict(events: list[Event], now: datetime | None = None) -> Prediction:
    now = now or datetime.now(timezone.utc)
    stats: BehaviorStats = compute_behavior_stats(events)

    last_pee = _last_event_of_type(events, EventType.PEE)
    last_food = _last_event_of_type(events, EventType.FOOD)
    last_sleep_end = _last_event_of_type(events, EventType.SLEEP_END)

    if last_pee is None:
        return Prediction(
            last_pee_at=None,
            minutes_since_last_pee=None,
            predicted_next_pee_at=None,
            probability_needs_out_now=0.3,
            best_moment_in_minutes=None,
            explanation="Brak historii siku - zaloguj pierwsze zdarzenie, żeby zacząć przewidywać.",
        )

    minutes_since_pee = (now - last_pee.timestamp).total_seconds() / 60
    candidate_starts = [(last_pee.timestamp, stats.avg_minutes_between_pee, "regularny odstęp między siku")]

    if last_food and last_food.timestamp > last_pee.timestamp:
        candidate_starts.append(
            (last_food.timestamp, stats.avg_minutes_after_food, "po jedzeniu")
        )
    if last_sleep_end and last_sleep_end.timestamp > last_pee.timestamp:
        candidate_starts.append(
            (last_sleep_end.timestamp, stats.avg_minutes_after_sleep, "po przebudzeniu")
        )

    trigger_time, wait_minutes, reason = min(
        candidate_starts, key=lambda c: c[0] + timedelta(minutes=c[1])
    )

    predicted_next_pee_at = trigger_time + timedelta(minutes=wait_minutes)
    minutes_until_predicted = (predicted_next_pee_at - now).total_seconds() / 60

    probability = _probability_from_minutes_overdue(-minutes_until_predicted)

    if minutes_until_predicted > 0:
        best_moment_text = f"Najlepszy moment za ok. {round(minutes_until_predicted)} min ({reason})."
        best_moment = minutes_until_predicted
    else:
        best_moment_text = f"Pies mógł już chcieć wyjść {abs(round(minutes_until_predicted))} min temu ({reason}) - sprawdź go."
        best_moment = 0.0

    confidence_note = (
        "Prognoza spersonalizowana na podstawie historii."
        if stats.is_personalized
        else "Za mało danych na spersonalizowaną prognozę - używamy typowych wartości dla szczeniaka."
    )

    return Prediction(
        last_pee_at=last_pee.timestamp,
        minutes_since_last_pee=round(minutes_since_pee, 1),
        predicted_next_pee_at=predicted_next_pee_at,
        probability_needs_out_now=probability,
        best_moment_in_minutes=round(best_moment, 1),
        explanation=f"{best_moment_text} {confidence_note}",
    )


def _probability_from_minutes_overdue(minutes_overdue: float) -> float:
    if minutes_overdue <= -20:
        return 0.05
    if minutes_overdue >= 20:
        return 0.95
    return round(0.05 + (minutes_overdue + 20) / 40 * 0.90, 2)