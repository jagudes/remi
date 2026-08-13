from datetime import date


def estimate_age_multiplier(birth_date: date | None, reference_date: date | None = None) -> float:

    if birth_date is None:
        return 1.0

    reference_date = reference_date or date.today()
    age_days = (reference_date - birth_date).days

    if age_days < 0:
        return 1.0

    age_weeks = age_days / 7

    if age_weeks < 12:
        return 0.45
    if age_weeks < 16:
        return 0.6
    if age_weeks < 24:
        return 0.75
    if age_weeks < 52:
        return 0.9
    return 1.0


def age_category_label(birth_date: date | None, reference_date: date | None = None) -> str:
    if birth_date is None:
        return "wiek nieznany"

    reference_date = reference_date or date.today()
    age_days = (reference_date - birth_date).days
    age_weeks = age_days / 7

    if age_weeks < 12:
        return "bardzo młody szczeniak (<12 tyg)"
    if age_weeks < 16:
        return "szczeniak (12-16 tyg)"
    if age_weeks < 24:
        return "szczeniak (16-24 tyg)"
    if age_weeks < 52:
        return "młody pies (do 12 mies)"
    return "dorosły pies"