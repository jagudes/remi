import { useState } from "react";

const API_URL = "http://localhost:8000";

interface Props {
  onLoggedIn: (token: string) => void;
}

export function AuthScreen({ onLoggedIn }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError(null);
    setLoading(true);
    try {
      if (mode === "register") {
        const res = await fetch(`${API_URL}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Błąd rejestracji");
        }
        setMode("login");
        setError("Konto utworzone — teraz się zaloguj.");
        return;
      }

      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Błąd logowania");
      }
      const data = await res.json();
      onLoggedIn(data.access_token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Coś poszło nie tak");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 320, margin: "60px auto" }}>
      <h1 style={{ fontSize: 24 }}>🐾 Remi</h1>
      <p style={{ color: "#7a7266" }}>
        {mode === "login" ? "Zaloguj się" : "Załóż konto"}
      </p>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{
          width: "100%",
          padding: 10,
          borderRadius: 8,
          border: "1px solid #ccc",
          marginBottom: 8,
          boxSizing: "border-box",
        }}
      />
      <input
        type="password"
        placeholder="Hasło"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{
          width: "100%",
          padding: 10,
          borderRadius: 8,
          border: "1px solid #ccc",
          marginBottom: 8,
          boxSizing: "border-box",
        }}
      />

      {error && (
        <p style={{ fontSize: 13, color: "#c0392b", marginBottom: 8 }}>{error}</p>
      )}

      <button
        onClick={handleSubmit}
        disabled={loading || !email || !password}
        style={{
          width: "100%",
          padding: 10,
          borderRadius: 8,
          border: "none",
          background: "#3d6b4f",
          color: "white",
          cursor: "pointer",
        }}
      >
        {mode === "login" ? "Zaloguj się" : "Zarejestruj się"}
      </button>

      <p style={{ textAlign: "center", marginTop: 12, fontSize: 13 }}>
        {mode === "login" ? (
          <>
            Nie masz konta?{" "}
            <a href="#" onClick={() => setMode("register")}>
              Zarejestruj się
            </a>
          </>
        ) : (
          <>
            Masz już konto?{" "}
            <a href="#" onClick={() => setMode("login")}>
              Zaloguj się
            </a>
          </>
        )}
      </p>
    </div>
  );
}