import type { Prediction } from "../types";

interface Props {
  prediction: Prediction | null;
  loading?: boolean;
}

function probabilityColor(p: number): string {
  if (p >= 0.7) return "#c0392b";
  if (p >= 0.4) return "#d98e04";
  return "#3d6b4f";
}

export function Dashboard({ prediction, loading }: Props) {
  if (loading) {
    return (
      <div style={{ padding: 16, border: "1px dashed #d8d2c4", borderRadius: 12, marginTop: 16, textAlign: "center", color: "#7a7266" }}>
          Ładowanie prognozy...
      </div>
    );
  }

  if (!prediction) {
    return (
      <div
        style={{
          border: "1px solid #d8d2c4",
          borderRadius: 12,
          padding: 16,
          background: "#fdfbf7",
          marginTop: 16,
          textAlign: "center",
          color: "#7a7266",
          fontSize: 14,
        }}
      >
        🐾 <strong>Brak danych do prognozy.</strong>
        <br />
        Zaloguj pierwsze zdarzenie (np. Siku lub Spacer) poniżej!
      </div>
    );
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