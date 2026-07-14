import { useEffect, useState } from "react";
import { getDogs, createDog, getEvents, logEvent } from "./api";
import type { Dog, DogEvent, EventType } from "./types";

const EVENT_LABELS: Record<EventType, string> = {
  pee: "🐕 Siku",
  poop: "💩 Kupa",
  food: "🍖 Jedzenie",
  sleep_start: "😴 Zasypia",
  sleep_end: "☀️ Budzi się",
  walk: "🚶 Spacer",
};

function App() {
  const [dogs, setDogs] = useState<Dog[]>([]);
  const [activeDogId, setActiveDogId] = useState<number | null>(null);
  const [events, setEvents] = useState<DogEvent[]>([]);
  const [newDogName, setNewDogName] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getDogs().then((data: Dog[]) => {
      setDogs(data);
      if (data.length > 0) setActiveDogId(data[0].id);
    });
  }, []);

  useEffect(() => {
    if (activeDogId !== null) {
      refreshEvents(activeDogId);
    }
  }, [activeDogId]);

  async function refreshEvents(dogId: number) {
    const data = await getEvents(dogId);
    setEvents(data);
  }

  async function handleAddDog() {
    if (!newDogName.trim()) return;
    setLoading(true);
    try {
      const dog = await createDog({ name: newDogName.trim() });
      setDogs((prev) => [...prev, dog]);
      setActiveDogId(dog.id);
      setNewDogName("");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogEvent(type: EventType) {
    if (activeDogId === null) return;
    await logEvent(activeDogId, type);
    refreshEvents(activeDogId);
  }

  const activeDog = dogs.find((d) => d.id === activeDogId);

  return (
    <div>
      <h1 style={{ fontSize: 24, marginBottom: 4 }}>🐾 Remi</h1>
      <p style={{ color: "#7a7266", marginTop: 0 }}>
        Śledzenie zachowania szczeniaka
      </p>

      {dogs.length === 0 && (
        <div style={{ marginTop: 24 }}>
          <p>Nie masz jeszcze dodanego psa. Dodaj pierwszego:</p>
          <input
            value={newDogName}
            onChange={(e) => setNewDogName(e.target.value)}
            placeholder="Imię psa"
            style={{
              padding: 10,
              borderRadius: 8,
              border: "1px solid #ccc",
              marginRight: 8,
            }}
          />
          <button
            onClick={handleAddDog}
            disabled={loading}
            style={{
              padding: "10px 16px",
              borderRadius: 8,
              border: "none",
              background: "#3d6b4f",
              color: "white",
              cursor: "pointer",
            }}
          >
            Dodaj
          </button>
        </div>
      )}

      {activeDog && (
        <>
          <h2 style={{ fontSize: 18, marginTop: 32 }}>
            Zaloguj zdarzenie dla: {activeDog.name}
          </h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 8,
              marginTop: 12,
            }}
          >
            {(Object.keys(EVENT_LABELS) as EventType[]).map((type) => (
              <button
                key={type}
                onClick={() => handleLogEvent(type)}
                style={{
                  padding: "14px 8px",
                  borderRadius: 10,
                  border: "1px solid #d8d2c4",
                  background: "white",
                  fontSize: 15,
                  cursor: "pointer",
                }}
              >
                {EVENT_LABELS[type]}
              </button>
            ))}
          </div>

          <h2 style={{ fontSize: 18, marginTop: 32 }}>Ostatnie zdarzenia</h2>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {events.map((ev) => (
              <li
                key={ev.id}
                style={{
                  padding: "10px 0",
                  borderBottom: "1px solid #e5e0d4",
                }}
              >
                {EVENT_LABELS[ev.type]} —{" "}
                {new Date(ev.timestamp).toLocaleString("pl-PL")}
              </li>
            ))}
            {events.length === 0 && <p>Brak zdarzeń.</p>}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;