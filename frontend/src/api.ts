import type {BreedInfo} from './types';
const API_URL = "http://localhost:8000";

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("remi_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function getDogs() {
  const res = await fetch(`${API_URL}/dogs`, {headers: authHeaders()});
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
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Nie udało się dodać psa");
  return res.json();
}

export async function getEvents(dogId: number) {
  const res = await fetch(`${API_URL}/dogs/${dogId}/events`, {headers: authHeaders()})
  ;
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
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ type, metadata }),
  });
  if (!res.ok) throw new Error("Nie udało się zapisać zdarzenia");
  return res.json();
}

export async function getPrediction(dogId: number) {
  const res = await fetch(`${API_URL}/dogs/${dogId}/prediction`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Nie udało się pobrać prognozy");
  return res.json();
}

export async function getSchedule(dogId: number) {
  const res = await fetch(`${API_URL}/dogs/${dogId}/schedule`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Nie udało się pobrać planu");
  return res.json();
}

export async function regenerateSchedule(dogId: number) {
  const res = await fetch(`${API_URL}/dogs/${dogId}/schedule/regenerate`, {
    method: "POST",
      headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Nie udało się przebudować planu");
  return res.json();
}


export async function fetchBreedInfo(dogId: number): Promise<BreedInfo> {
  const response = await fetch(`${API_URL}/dogs/${dogId}/breed-info`, {headers: authHeaders()});
  if (!response.ok) {
    throw new Error('Nie udało się połączyć z serwerem');
  }
  return response.json();
}