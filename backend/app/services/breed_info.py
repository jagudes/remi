from dataclasses import dataclass
import httpx
import os

THE_DOG_API_URL = "https://api.thedogapi.com/v1/breeds/search"
REQUEST_TIMEOUT_SECONDS = 5.0
DOG_API_KEY = os.getenv("THE_DOG_API_KEY", "live_xvNU7GRqN3fISkfbuya1goJ3HplHJ80LtPO4VXYPmbXTQCqoTFoTf8wNJDCHsMbe")

HIGH_ENERGY_KEYWORDS = ["active", "energetic", "playful", "lively", "agile"]
LOW_ENERGY_KEYWORDS = ["calm", "docile", "quiet", "gentle", "mellow"]


@dataclass
class BreedInfo:
    name: str
    temperament: str | None
    bred_for: str | None
    life_span: str | None
    weight_metric: str | None
    breed_group: str | None
    found: bool
    error: str | None = None


def fetch_breed_info(breed_name: str) -> BreedInfo:
    if not breed_name or not breed_name.strip():
        return BreedInfo(
            name=breed_name,
            temperament=None,
            bred_for=None,
            life_span=None,
            weight_metric=None,
            breed_group=None,
            found=False,
            error="Nie podano rasy psa.",
        )
    headers = {
        "x-api-key": DOG_API_KEY,
        "User-Agent": "FastAPI-DogApp/1.0"
    }

    try:
        response = httpx.get(
            THE_DOG_API_URL,
            params={"q": breed_name},
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        results = response.json()
    except httpx.HTTPError as e:
        return BreedInfo(
            name=breed_name,
            temperament=None,
            bred_for=None,
            life_span=None,
            weight_metric=None,
            breed_group=None,
            found=False,
            error=f"Nie udało się pobrać informacji o rasie ({e}).",
        )

    if not results:
        return BreedInfo(
            name=breed_name,
            temperament=None,
            bred_for=None,
            life_span=None,
            weight_metric=None,
            breed_group=None,
            found=False,
            error="Nie znaleziono tej rasy w bazie.",
        )

    match = results[0]
    weight = match.get("weight", {}).get("metric")

    return BreedInfo(
        name=match.get("name", breed_name),
        temperament=match.get("temperament"),
        bred_for=match.get("bred_for"),
        life_span=match.get("life_span"),
        weight_metric=f"{weight} kg" if weight else None,
        breed_group=match.get("breed_group"),
        found=True,
    )


def estimate_energy_multiplier(temperament: str | None) -> float:
    if not temperament:
        return 1.0

    lower = temperament.lower()

    if any(word in lower for word in HIGH_ENERGY_KEYWORDS):
        return 0.85
    if any(word in lower for word in LOW_ENERGY_KEYWORDS):
        return 1.15
    return 1.0