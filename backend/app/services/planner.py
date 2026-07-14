from dataclasses import dataclass, field
from datetime import datetime, timedelta, time

from app.models.event import Event
from app.services.analytics import BehaviorStats, compute_behavior_stats, count_recent_accidents

ACCIDENT_THRESHOLD_FOR_ADAPTATION = 3

DEFAULT_WAKE_UP_TIME = time(hour=7, minute=0)
DEFAULT_NAP_INTERVAL_MIN = 120
DEFAULT_FOOD_INTERVAL_MIN = 240
DAY_LENGTH_HOURS = 14


@dataclass
class ScheduleBlock:
    type: str
    time_str: str
    reason: str


@dataclass
class GeneratedSchedule:
    blocks: list[ScheduleBlock] = field(default_factory=list)
    is_adapted: bool = False


def generate_schedule(
    events: list[Event],
    wake_up_time: time = DEFAULT_WAKE_UP_TIME,
    reference_date: datetime | None = None,
) -> GeneratedSchedule:
    stats: BehaviorStats = compute_behavior_stats(events)
    recent_accidents = count_recent_accidents(events)
    is_adapted = recent_accidents >= ACCIDENT_THRESHOLD_FOR_ADAPTATION

    walk_after_food_min = stats.avg_minutes_after_food
    walk_after_sleep_min = stats.avg_minutes_after_sleep
    between_walks_min = stats.avg_minutes_between_pee

    if is_adapted:
        walk_after_food_min *= 0.7
        walk_after_sleep_min *= 0.7
        between_walks_min *= 0.6

    reference_date = reference_date or datetime.now()
    day_start = datetime.combine(reference_date.date(), wake_up_time)

    blocks: list[ScheduleBlock] = []
    blocks.append(ScheduleBlock(type="wake_up", time_str=_fmt(day_start), reason="pobudka"))
    blocks.append(
        ScheduleBlock(
            type="walk",
            time_str=_fmt(day_start + timedelta(minutes=walk_after_sleep_min)),
            reason="spacer po przebudzeniu",
        )
    )

    current_time = day_start
    day_end = day_start + timedelta(hours=DAY_LENGTH_HOURS)

    next_food_at = current_time + timedelta(minutes=30)
    next_nap_at = current_time + timedelta(minutes=DEFAULT_NAP_INTERVAL_MIN)
    next_walk_at = current_time + timedelta(minutes=between_walks_min)

    events_queue = []
    while next_food_at < day_end:
        events_queue.append(("food", next_food_at))
        next_food_at += timedelta(minutes=DEFAULT_FOOD_INTERVAL_MIN)

    while next_nap_at < day_end:
        events_queue.append(("nap", next_nap_at))
        next_nap_at += timedelta(minutes=DEFAULT_NAP_INTERVAL_MIN)

    while next_walk_at < day_end:
        events_queue.append(("walk", next_walk_at))
        next_walk_at += timedelta(minutes=between_walks_min)

    events_queue.sort(key=lambda e: e[1])

    for block_type, block_time in events_queue:
        if block_type == "food":
            blocks.append(ScheduleBlock(type="food", time_str=_fmt(block_time), reason="posiłek"))
            blocks.append(
                ScheduleBlock(
                    type="walk",
                    time_str=_fmt(block_time + timedelta(minutes=walk_after_food_min)),
                    reason="spacer po jedzeniu",
                )
            )
        elif block_type == "nap":
            blocks.append(ScheduleBlock(type="nap", time_str=_fmt(block_time), reason="drzemka"))
        elif block_type == "walk":
            blocks.append(
                ScheduleBlock(type="walk", time_str=_fmt(block_time), reason="regularny spacer")
            )

    # Sortujemy cały plan chronologicznie i usuwamy duplikaty zbyt blisko siebie (<10 min)
    blocks.sort(key=lambda b: b.time_str)
    blocks = _remove_near_duplicates(blocks)

    return GeneratedSchedule(blocks=blocks, is_adapted=is_adapted)


def _fmt(dt: datetime) -> str:
    return dt.strftime("%H:%M")


MIN_GAP_BETWEEN_WALKS_MIN = 45


def _remove_near_duplicates(blocks: list[ScheduleBlock], min_gap_min: int = 10) -> list[ScheduleBlock]:
    if not blocks:
        return blocks

    result = [blocks[0]]
    for block in blocks[1:]:
        prev_time = datetime.strptime(result[-1].time_str, "%H:%M")
        curr_time = datetime.strptime(block.time_str, "%H:%M")
        gap = (curr_time - prev_time).total_seconds() / 60

        if block.type == "walk" and result[-1].type == "walk":
            if gap < MIN_GAP_BETWEEN_WALKS_MIN:
                continue
            result.append(block)
        elif gap >= min_gap_min or block.type != result[-1].type:
            result.append(block)
    return result