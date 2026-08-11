export type EventType = "pee" | "poop" | "food" | "sleep_start" | "sleep_end" | "walk";

export interface Dog {
  id: number;
  name: string;
  breed: string | null;
  birth_date: string | null;
  weight_kg: number | null;
}

export interface DogEvent {
  id: number;
  dog_id: number;
  type: EventType;
  timestamp: string;
  metadata_json: Record<string, unknown> | null;
}

export interface Prediction {
  last_pee_at: string | null;
  minutes_since_last_pee: number | null;
  predicted_next_pee_at: string | null;
  probability_needs_out_now: number;
  best_moment_in_minutes: number | null;
  explanation: string;
}

export interface ScheduleBlock {
  type: "wake_up" | "walk" | "food" | "nap";
  time: string;
  reason: string;
}

export interface Schedule {
  id: number;
  dog_id: number;
  date: string;
  blocks: ScheduleBlock[];
  generated_at: string;
  is_adapted: boolean;
}

export interface BreedInfo {
  name: string;
  temperament: string | null;
  bred_for: string | null;
  life_span: string | null;
  weight_metric: string | null;
  breed_group: string | null;
  found: boolean;
  error: string | null;
}