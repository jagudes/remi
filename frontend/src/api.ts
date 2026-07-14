const API_URL = "http://localhost:8000";

export async function getDogs() {
  const res = await fetch(`${API_URL}/dogs`);
  if (!res.ok) throw new Error("Nie udało się pobrać psów");
  return res.json();
}

export async function createDog(data: {
  name: string;
  breed?: string;
  weight_kg?: number;
}) {
  const res = await fetch(`${API_URL}/dogs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Nie udało się dodać psa");
  return res.json();
}

export async function getEvents(dogId: number) {
  const res = await fetch(`${API_URL}/dogs/${dogId}/events`);
  if (!res.ok) throw new Error("Nie udało się pobrać zdarzeń");
  return res.json();
}

export async function logEvent(
  dogId: number,
  type: string,
  metadata?: Record<string, unknown>
) {
  const res = await fetch(`${API_URL}/dogs/${dogId}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, metadata }),
  });
  if (!res.ok) throw new Error("Nie udało się zapisać zdarzenia");
  return res.json();
}