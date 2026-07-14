import type { Prediction } from "../types";

interface Props {
  prediction: Prediction | null;
}

function probabilityColor(p: number): string {
  if (p >= 0.7) return "#c0392b";
  if (p >= 0.4) return "#d98e04";
  return "#3d6b4f";
}

export function Dashboard({ prediction }: Props) {
  if (!prediction) {
    return <p>Ładowanie prognozy...</p>;
  }

  const probabilityPercent = Math.round(
    prediction.probability_needs_out_now * 100
  );

  return (
    <div
      style={{
        border: "1px solid #d8d2c4",
        borderRadius: 12,
        padding: 16,
        background: "white",
        marginTop: 16,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span style={{ color: "#7a7266", fontSize: 13 }}>
          Ostatnie siku
        </span>
        <span style={{ fontSize: 13 }}>
          {prediction.minutes_since_last_pee !== null
            ? `${Math.round(prediction.minutes_since_last_pee)} min temu`
            : "brak danych"}
        </span>
      </div>

      <div
        style={{
          marginTop: 12,
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <div
          style={{
            width: 56,
            height: 56,
            borderRadius: "50%",
            border: `4px solid ${probabilityColor(
              prediction.probability_needs_out_now
            )}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 14,
          }}
        >
          {probabilityPercent}%
        </div>
        <div>
          <div style={{ fontSize: 13, color: "#7a7266" }}>
            Prawdopodobieństwo, że chce wyjść teraz
          </div>
        </div>
      </div>

      <p style={{ marginTop: 12, fontSize: 14, lineHeight: 1.4 }}>
        {prediction.explanation}
      </p>
    </div>
  );
}