from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from app.models.event import Event, EventType
from app.services.analytics import BehaviorStats, compute_behavior_stats
from app.services.ml_features import build_training_table

MIN_ROWS_FOR_ML = 15


@dataclass
class Prediction:
    last_pee_at: datetime | None
    minutes_since_last_pee: float | None
    predicted_next_pee_at: datetime | None
    probability_needs_out_now: float
    best_moment_in_minutes: float | None
    explanation: str

def _ensure_naive(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def _last_event_of_type(events: list[Event], event_type: EventType) -> Event | None:
    matching = [e for e in events if e.type == event_type]
    if not matching:
        return None
    return max(matching, key=lambda e: e.timestamp)


def _train_model(training_df: pd.DataFrame) -> RandomForestRegressor:
    clean_df = training_df.dropna(subset=["gap_to_next_pee_minutes"]).fillna(0)

    X = pd.get_dummies(clean_df[["trigger_type" , "hour_of_day", "minutes_since_prev_pee"]])
    y = clean_df["gap_to_next_pee_minutes"]

    model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X, y)
    return model, X.columns.tolist()


def _predict_with_ml(
    model: RandomForestRegressor,
    feature_columns: list[str],
    trigger_type: str,
    hour_of_day: int,
    minutes_since_prev_pee: float,
) -> float:
    row = pd.DataFrame(
        [{"trigger_type": trigger_type, "hour_of_day": hour_of_day, "minutes_since_prev_pee": minutes_since_prev_pee}]
    )
    row_encoded = pd.get_dummies(row)
    row_encoded = row_encoded.reindex(columns=feature_columns, fill_value=0)
    return float(model.predict(row_encoded)[0])


def predict(
    events: list[Event],
    now: datetime | None = None,
    energy_multiplier: float = 1.0,
) -> Prediction:
    now = _ensure_naive(now or datetime.now(timezone.utc))

    for e in events:
        e.timestamp = _ensure_naive(e.timestamp)

    stats: BehaviorStats = compute_behavior_stats(events, energy_multiplier=energy_multiplier)

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

    training_df = build_training_table(events)
    use_ml = len(training_df) >= MIN_ROWS_FOR_ML

    candidate_starts = [(last_pee.timestamp, EventType.PEE.value)]
    if last_food and last_food.timestamp > last_pee.timestamp:
        candidate_starts.append((last_food.timestamp, EventType.FOOD.value))
    if last_sleep_end and last_sleep_end.timestamp > last_pee.timestamp:
        candidate_starts.append((last_sleep_end.timestamp, EventType.SLEEP_END.value))

    ml_success = False
    if use_ml:
        try:
            model, feature_columns = _train_model(training_df)

            scored_candidates = []
            for trigger_time, trigger_type in candidate_starts:
                minutes_since_prev_pee = (trigger_time - last_pee.timestamp).total_seconds() / 60
                wait_minutes = _predict_with_ml(
                    model, feature_columns, trigger_type, trigger_time.hour, max(minutes_since_prev_pee, 0)
                )
                wait_minutes = max(wait_minutes, 0)
                scored_candidates.append((trigger_time, wait_minutes, _reason_label(trigger_type)))

            trigger_time, wait_minutes, reason = min(
                scored_candidates, key=lambda c: c[0] + timedelta(minutes=c[1])
            )
            confidence_note = f"Prognoza z modelu ML (wytrenowanego na {len(training_df)} zapisanych sytuacjach)."
            ml_success = True
        except Exception as err:
            print(f"ML predict error - {err}")
            ml_success = False

    if not ml_success:
        reason_to_minutes = {
            EventType.FOOD.value: stats.avg_minutes_after_food,
            EventType.SLEEP_END.value: stats.avg_minutes_after_sleep,
            EventType.PEE.value: stats.avg_minutes_between_pee,
        }
        scored_candidates = [
            (t_time, reason_to_minutes[t_type], _reason_label(t_type))
            for t_time, t_type in candidate_starts
        ]
        trigger_time, wait_minutes, reason = min(
            scored_candidates, key=lambda c: c[0] + timedelta(minutes=c[1])
        )
        confidence_note = (
            f"Za mało danych na model ML ({len(training_df)}/{MIN_ROWS_FOR_ML} potrzebnych) "
            "- używamy uśrednionych wzorców."
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

    return Prediction(
        last_pee_at=last_pee.timestamp,
        minutes_since_last_pee=round(minutes_since_pee, 1),
        predicted_next_pee_at=predicted_next_pee_at,
        probability_needs_out_now=probability,
        best_moment_in_minutes=round(best_moment, 1),
        explanation=f"{best_moment_text} {confidence_note}",
    )


def _reason_label(trigger_type: str) -> str:
    return {
        EventType.FOOD.value: "po jedzeniu",
        EventType.SLEEP_END.value: "po przebudzeniu",
        EventType.PEE.value: "regularny odstęp między siku",
    }[trigger_type]


def _probability_from_minutes_overdue(minutes_overdue: float) -> float:
    if minutes_overdue <= -20:
        return 0.05
    if minutes_overdue >= 20:
        return 0.95
    return round(0.05 + (minutes_overdue + 20) / 40 * 0.90, 2)