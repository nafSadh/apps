"""
Unified match schema + team-name canonicalization shared by every source adapter.

Every adapter (538 SPI, football-data.co.uk, StatsBomb, the martj42 base) emits
rows of this one shape so the corpus builder and the transformer can treat all
sources identically. Richness fields are optional — set them to None when a
source doesn't carry them, and let the model mask them (NEVER drop a match just
because it lacks xG).

Team names differ across sources ("USA" vs "United States", "Korea Republic" vs
"South Korea", "Côte d'Ivoire" vs "Ivory Coast"). `canon()` maps source names to
the martj42 international spelling (our base). The ALIASES seed below is
deliberately small and extensible — `build_corpus.py` reports any unmapped names
so you can grow it.
"""

from dataclasses import dataclass, asdict, fields
from typing import Optional
import csv
import re
import unicodedata

# ---- unified row -----------------------------------------------------------
@dataclass
class UnifiedMatch:
    date: str            # YYYY-MM-DD
    home: str            # canonical team name
    away: str
    home_score: Optional[int]
    away_score: Optional[int]
    neutral: Optional[bool]
    competition: str     # free text (e.g. "Premier League", "FIFA World Cup")
    source: str          # "intl_base" | "spi_intl" | "spi_club" | "football_data" | "statsbomb"
    is_intl: bool        # international fixture (vs club)
    # ---- optional richness (None when unavailable) ----
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None
    home_shots: Optional[float] = None
    away_shots: Optional[float] = None
    home_sot: Optional[float] = None
    away_sot: Optional[float] = None
    home_poss: Optional[float] = None
    away_poss: Optional[float] = None

    def key(self):
        return (self.date, self.home, self.away)


CSV_FIELDS = [f.name for f in fields(UnifiedMatch)]


def write_corpus(rows, path):
    rows = sorted(rows, key=lambda r: (r.date, r.home, r.away))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))
    return len(rows)


def read_corpus(path):
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        for d in csv.DictReader(f):
            out.append(UnifiedMatch(
                date=d["date"], home=d["home"], away=d["away"],
                home_score=_int(d["home_score"]), away_score=_int(d["away_score"]),
                neutral=_bool(d["neutral"]), competition=d["competition"],
                source=d["source"], is_intl=_bool(d["is_intl"]),
                home_xg=_float(d["home_xg"]), away_xg=_float(d["away_xg"]),
                home_shots=_float(d["home_shots"]), away_shots=_float(d["away_shots"]),
                home_sot=_float(d["home_sot"]), away_sot=_float(d["away_sot"]),
                home_poss=_float(d["home_poss"]), away_poss=_float(d["away_poss"])))
    return out


def _int(s):
    s = (s or "").strip()
    return int(float(s)) if s not in ("", "NA", "None") else None


def _float(s):
    s = (s or "").strip()
    return float(s) if s not in ("", "NA", "None") else None


def _bool(s):
    return str(s).strip().lower() in ("true", "1", "yes")


# ---- team-name canonicalization -------------------------------------------
# source spelling -> martj42 canonical. Extend freely.
ALIASES = {
    "usa": "United States", "united states of america": "United States",
    "korea republic": "South Korea", "korea, republic of": "South Korea",
    "republic of korea": "South Korea", "south korea": "South Korea",
    "korea dpr": "North Korea", "korea, dpr": "North Korea", "north korea": "North Korea",
    "ir iran": "Iran", "iran islamic republic of": "Iran",
    "china pr": "China PR", "china": "China PR",
    "cote d'ivoire": "Ivory Coast", "côte d'ivoire": "Ivory Coast",
    "ivory coast": "Ivory Coast",
    "cape verde islands": "Cape Verde", "cabo verde": "Cape Verde",
    "czechia": "Czech Republic",
    "dr congo": "DR Congo", "congo dr": "DR Congo",
    "congo democratic republic of": "DR Congo", "democratic republic of congo": "DR Congo",
    "bosnia": "Bosnia and Herzegovina", "bosnia-herzegovina": "Bosnia and Herzegovina",
    "ireland": "Republic of Ireland", "republic of ireland": "Republic of Ireland",
    "curacao": "Curaçao",
    "turkiye": "Turkey", "türkiye": "Turkey",
    "north macedonia": "North Macedonia", "macedonia": "North Macedonia",
    "cabo": "Cape Verde",
    "saudi": "Saudi Arabia",
    "uae": "United Arab Emirates",
}


def _strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def _norm(name):
    s = name.strip()
    s = re.sub(r"\s+", " ", s)
    s = _strip_accents(s).lower()
    return s


# names we keep exactly as martj42 spells them even though _norm differs
_KEEP = {"curaçao": "Curaçao"}

# canonical vocabulary (normalized form -> canonical spelling), seeded from the
# martj42 base by register_canonical(); names matching it are NOT flagged unmapped.
_CANON_BY_NORM = {}
_unmapped = set()


def register_canonical(names):
    """Declare the set of canonical team spellings (the martj42 base names)."""
    for nm in names:
        _CANON_BY_NORM[_norm(nm)] = nm


def canon(name):
    """Map a source team name to the martj42 canonical spelling."""
    if name is None:
        return None
    n = _norm(name)
    if n in ALIASES:
        return ALIASES[n]
    if n in _KEEP:
        return _KEEP[n]
    if n in _CANON_BY_NORM:
        return _CANON_BY_NORM[n]
    # unknown: keep the cleaned name and record it for the unmapped report
    guess = re.sub(r"\s+", " ", name.strip())
    _unmapped.add(guess)
    return guess


def unmapped_names():
    """Names canon() fell through on — review these and add to ALIASES."""
    return sorted(_unmapped)
