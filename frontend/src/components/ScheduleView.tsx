import type { Schedule, ScheduleBlock } from "../types";

interface Props {
  schedule: Schedule | null;
  onRegenerate: () => void;
}

const BLOCK_ICONS: Record<ScheduleBlock["type"], string> = {
  wake_up: "☀️",
  walk: "🚶",
  food: "🍖",
  nap: "😴",
};

const BLOCK_COLORS: Record<ScheduleBlock["type"], string> = {
  wake_up: "#f4c542",
  walk: "#3d6b4f",
  food: "#c0632e",
  nap: "#5a6b8c",
};

export function ScheduleView({ schedule, onRegenerate }: Props) {
  if (!schedule) {
    return <p>Ładowanie planu...</p>;
  }

  return (
    <div style={{ marginTop: 16 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h2 style={{ fontSize: 18, margin: 0 }}>Plan dnia</h2>
        <button
          onClick={onRegenerate}
          style={{
            padding: "6px 12px",
            borderRadius: 8,
            border: "1px solid #d8d2c4",
            background: "white",
            fontSize: 13,
            cursor: "pointer",
          }}
        >
          Przebuduj plan
        </button>
      </div>

      {schedule.is_adapted && (
        <p
          style={{
            fontSize: 13,
            color: "#c0392b",
            background: "#fbeae7",
            padding: "8px 12px",
            borderRadius: 8,
            marginTop: 8,
          }}
        >
          Plan został zagęszczony — ostatnio było więcej wypadków w domu niż
          zwykle.
        </p>
      )}

      <div
        style={{
          display: "flex",
          gap: 10,
          overflowX: "auto",
          padding: "16px 4px",
          marginTop: 4,
          scrollSnapType: "x mandatory",
        }}
      >
        {schedule.blocks.map((block, i) => (
          <div
            key={i}
            style={{
              flex: "0 0 auto",
              width: 96,
              scrollSnapAlign: "start",
              background: "white",
              border: "1px solid #e5e0d4",
              borderRadius: 12,
              padding: "10px 8px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: BLOCK_COLORS[block.type],
                margin: "0 auto 6px",
              }}
            />
            <div style={{ fontSize: 13, fontWeight: 700 }}>{block.time}</div>
            <div style={{ fontSize: 20, margin: "4px 0" }}>
              {BLOCK_ICONS[block.type]}
            </div>
            <div style={{ fontSize: 11, color: "#7a7266", lineHeight: 1.3 }}>
              {block.reason}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}