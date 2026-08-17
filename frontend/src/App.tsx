import { useEffect, useState } from "react";
import { getDogs, createDog, getEvents, logEvent, getPrediction, getSchedule, regenerateSchedule, fetchBreedInfo } from "./api";
import type { Dog, DogEvent, EventType, Prediction, Schedule, BreedInfo } from "./types";
import { Dashboard } from "./components/Dashboard";
import { ScheduleView } from "./components/ScheduleView";
import { AuthScreen } from "./components/AuthScreen";


const EVENT_LABELS: Record<EventType, string> = {
  pee: "🐕 Siku",
  poop: "💩 Kupa",
  food: "🍖 Jedzenie",
  sleep_start: "😴 Zasypia",
  sleep_end: "☀️ Budzi się",
  walk: "🚶 Spacer",
};

function App() {
    const [token, setToken] = useState<string | null>(
    localStorage.getItem("remi_token")
  );
  const [dogs, setDogs] = useState<Dog[]>([]);
  const [activeDogId, setActiveDogId] = useState<number | null>(null);
  const [events, setEvents] = useState<DogEvent[]>([]);
  const [newDogName, setNewDogName] = useState("");
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [schedule, setSchedule] = useState<Schedule | null>(null);

  const [breedInfo, setBreedInfo] = useState<BreedInfo | null>(null);
  const [breedLoading, setBreedLoading] = useState(false);

  useEffect(() => {
      if (!token) return;

    getDogs().then((data: Dog[]) => {
      setDogs(data);
      if (data.length > 0) setActiveDogId(data[0].id);
    });
  }, [token]);

useEffect(() => {
  if (activeDogId !== null) {
    refreshEvents(activeDogId);
    refreshPrediction(activeDogId);
    refreshSchedule(activeDogId);
    refreshBreedInfo(activeDogId);
  }
}, [activeDogId]);

async function refreshBreedInfo(dogId: number) {
    setBreedLoading(true);
    try {
      const data = await fetchBreedInfo(dogId);
      setBreedInfo(data);
    } catch (err) {
      console.error("Błąd pobierania rasy:", err);
    } finally {
      setBreedLoading(false);
    }
  }

async function refreshSchedule(dogId: number) {
  const data = await getSchedule(dogId);
  setSchedule(data);
}

async function handleRegenerateSchedule() {
  if (activeDogId === null) return;
  const data = await regenerateSchedule(activeDogId);
  setSchedule(data);
}

async function refreshPrediction(dogId: number) {
  try {
    const data = await getPrediction(dogId);
    setPrediction(data);
  } catch (err) {
    console.error("Błąd pobierania prognozy:", err);
    setPrediction(null);
  }
}

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
    refreshPrediction(activeDogId);

  }

  const activeDog = dogs.find((d) => d.id === activeDogId);

    if (!token) {
    return (
      <AuthScreen
        onLoggedIn={(newToken) => {
          localStorage.setItem("remi_token", newToken);
          setToken(newToken);
        }}
      />
    );
  }

  return (
    <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <h1 style={{ fontSize: 24, marginBottom: 4 }}>🐾 Remi</h1>
        <button
          onClick={() => {
            localStorage.removeItem("remi_token");
            setToken(null);
          }}
          style={{
            fontSize: 12,
            padding: "4px 10px",
            borderRadius: 6,
            border: "1px solid #d8d2c4",
            background: "white",
            cursor: "pointer",
          }}
        >
          Wyloguj
        </button>
      </div>
      <p style={{ color: "#7a7266", marginTop: 0 }}>
        Śledzenie zachowania szczeniaka
      </p>
{dogs.length > 0 && (
        <div
          style={{
            margin: "16px 0",
            padding: 12,
            background: "#fdfbf7",
            borderRadius: 10,
            border: "1px solid #e5e0d4",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <div>
            <label htmlFor="dog-select" style={{ marginRight: 8, fontSize: 14, fontWeight: "bold" }}>
              Wybierz psa:
            </label>
            <select
              id="dog-select"
              value={activeDogId ?? ""}
              onChange={(e) => setActiveDogId(Number(e.target.value))}
              style={{
                padding: "6px 12px",
                borderRadius: 8,
                border: "1px solid #d8d2c4",
                background: "white",
                fontSize: 14,
                cursor: "pointer",
              }}
            >
              {dogs.map((dog) => (
                <option key={dog.id} value={dog.id}>
                  {dog.name} (ID: {dog.id})
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", gap: 6 }}>
            <input
              value={newDogName}
              onChange={(e) => setNewDogName(e.target.value)}
              placeholder="Imię nowego psa"
              style={{
                padding: "6px 10px",
                borderRadius: 6,
                border: "1px solid #ccc",
                fontSize: 13,
              }}
            />
            <button
              onClick={handleAddDog}
              disabled={loading}
              style={{
                padding: "6px 12px",
                borderRadius: 6,
                border: "none",
                background: "#3d6b4f",
                color: "white",
                cursor: "pointer",
                fontSize: 13,
              }}
            >
              + Dodaj
            </button>
          </div>
        </div>
      )}

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
            <Dashboard prediction={prediction} />
<ScheduleView schedule={schedule} onRegenerate={handleRegenerateSchedule} />
{breedLoading ? (
            <p style={{ color: "#7a7266", fontSize: 14 }}>Ładowanie informacji o rasie...</p>
          ) : breedInfo && !breedInfo.error ? (
            <div
              style={{
                marginTop: 20,
                padding: 16,
                borderRadius: 12,
                background: "#f7f5f0",
                border: "1px solid #e5e0d4",
              }}
            >
              <h3 style={{ margin: "0 0 8px 0", fontSize: 16, color: "#3d6b4f" }}>
                ℹ️ Informacje o rasie: {breedInfo.name}
              </h3>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 14, color: "#4a453e", lineHeight: "1.6" }}>
                {breedInfo.temperament && <li><strong>Temperament:</strong> {breedInfo.temperament}</li>}
                {breedInfo.bred_for && <li><strong>Rola:</strong> {breedInfo.bred_for}</li>}
                {breedInfo.life_span && <li><strong>Długość życia:</strong> {breedInfo.life_span}</li>}
                {breedInfo.weight_metric && <li><strong>Waga:</strong> {breedInfo.weight_metric}</li>}
                {breedInfo.breed_group && <li><strong>Grupa:</strong> {breedInfo.breed_group}</li>}
              </ul>
            </div>
          ) : breedInfo?.error ? (
            <p style={{ color: "#a84242", fontSize: 13, marginTop: 12 }}>
              Błąd rasy: {breedInfo.error}
            </p>
          ) : null}



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