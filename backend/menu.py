"""Menue-Stammdaten laden und Artikelnummern aufloesen.

`menu.json` hat KEINEN eindeutigen `nr`-Namensraum: dieselbe Nummer taucht in
mehreren Sektionen auf (z. B. nr 5 = "Souvflaki" in `gerichte` UND
"Olivenmarmelade" in `vorspeisen_kalt`), und nr 3 kommt sogar doppelt in
`gerichte` vor. Deshalb matcht `resolve()` primaer ueber `nr`, nutzt bei
Mehrdeutigkeit den Bon-Namen als Gegenprobe (Handoff §3) und meldet solche
Faelle als `ambiguous`, damit der Betrieb "nie blind" laeuft (Handoff §1/§2).
"""
from __future__ import annotations

import difflib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

MENU_PATH = Path(__file__).resolve().parent.parent / "menu.json"

# Sektionen, deren Eintraege in den flachen Lookup wandern.
_DISH_ARRAYS = ("gerichte", "vorspeisen_kalt", "beilagen", "dessert")

VORSPEISE_KATEGORIEN = {"vorspeise_kalt", "vorspeise_warm", "suppe"}

GAENGE = ("Vorspeise", "Hauptgang", "Dessert")


@dataclass(frozen=True)
class Dish:
    nr: int
    name: str
    sektion: str
    station: str
    gang: str
    prep_seed_min: int
    garstufe: bool
    kategorie: Optional[str] = None


def _gang_for(sektion: str, kategorie: Optional[str]) -> str:
    """Fallback-Ableitung, falls ein Eintrag kein `gang`-Feld traegt."""
    if sektion == "dessert":
        return "Dessert"
    if sektion == "vorspeisen_kalt":
        return "Vorspeise"
    if sektion == "beilagen":
        return "Hauptgang"
    if kategorie in VORSPEISE_KATEGORIEN:
        return "Vorspeise"
    return "Hauptgang"


def _to_dish(entry: dict, sektion: str) -> Dish:
    return Dish(
        nr=int(entry["nr"]),
        name=entry["name"],
        sektion=sektion,
        station=entry.get("station", "kalt"),
        gang=entry.get("gang") or _gang_for(sektion, entry.get("kategorie")),
        prep_seed_min=int(entry.get("prep_seed_min", 5)),
        garstufe=bool(entry.get("garstufe", False)),
        kategorie=entry.get("kategorie"),
    )


@lru_cache(maxsize=1)
def load_menu(path: Optional[str] = None) -> dict[int, list[Dish]]:
    """Flacher Lookup `nr -> [Dish, ...]`. Mehrere Kandidaten = Kollision."""
    p = Path(path) if path else MENU_PATH
    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    lookup: dict[int, list[Dish]] = {}
    for array_key in _DISH_ARRAYS:
        for entry in data.get(array_key, []):
            dish = _to_dish(entry, array_key)
            lookup.setdefault(dish.nr, []).append(dish)
    return lookup


def _best_by_name(name: str, candidates: list[Dish]) -> Optional[Dish]:
    # Case-insensitiv: echte Bons schreiben Namen GROSS, das Menue gemischt.
    names = [c.name.lower() for c in candidates]
    match = difflib.get_close_matches(name.lower(), names, n=1, cutoff=0.6)
    if match:
        for c in candidates:
            if c.name.lower() == match[0]:
                return c
    return None


@dataclass(frozen=True)
class Resolution:
    dish: Optional[Dish]   # None = unbekannte Nummer
    ambiguous: bool        # True = Kollision (auch wenn per Name aufgeloest)
    unknown: bool          # True = nr nicht im Menue


def _dish_by_name_global(name: str, path: Optional[str]) -> Optional[Dish]:
    """Sucht ueber ALLE Gerichte nach dem besten Namenstreffer (fuer Positionen
    ohne Nr, z. B. Beilagen wie 'REIS')."""
    alle: list[Dish] = [d for cands in load_menu(path).values() for d in cands]
    treffer = difflib.get_close_matches(
        name.lower(), [d.name.lower() for d in alle], n=1, cutoff=0.7)
    if treffer:
        for d in alle:
            if d.name.lower() == treffer[0]:
                return d
    return None


def resolve(nr: Optional[int], name: Optional[str] = None,
            path: Optional[str] = None) -> Resolution:
    """Loest eine Artikelnummer gegen das Menue auf.

    - leere nr + Name      -> Namens-Fallback (Beilagen/Extras ohne Nr)
    - unbekannte/leere nr  -> unknown=True, dish=None
    - eindeutige nr        -> dish gesetzt, ambiguous=False
    - Kollision            -> Namens-Gegenprobe; ambiguous=True
    """
    if nr is None:
        if name:
            dish = _dish_by_name_global(name, path)
            if dish is not None:
                return Resolution(dish=dish, ambiguous=False, unknown=False)
        return Resolution(dish=None, ambiguous=False, unknown=True)

    lookup = load_menu(path)
    candidates = lookup.get(int(nr))
    if not candidates:
        return Resolution(dish=None, ambiguous=False, unknown=True)
    if len(candidates) == 1:
        return Resolution(dish=candidates[0], ambiguous=False, unknown=False)

    # Kollision: erst Namens-Gegenprobe, sonst Hauptgericht bevorzugen.
    chosen = _best_by_name(name, candidates) if name else None
    if chosen is None:
        gerichte = [c for c in candidates if c.sektion == "gerichte"]
        chosen = gerichte[0] if gerichte else candidates[0]
    return Resolution(dish=chosen, ambiguous=True, unknown=False)
