"""Bon-Simulator (Handoff §9.2 / §12.2) — im echten Schultes-Küchenbon-Format.

Erzeugt Bons wie der Schultes-Küchendrucker (siehe parser.py): Kopf mit Datum/
Uhrzeit, `Tisch <n>`, Positionen `<menge>  <nr> <NAME>   *<preis>`, Garstufe als
eigene Zeile, gelegentlich Notiz/Beilage, Gang-Marker und Fuß `K 4`.
Ersetzt in V1 die Demo-Steuerung „＋ Bon"; die reale serielle Quelle wird später
hinter `bonsource.PrinterTcpSource` bzw. einem Serial-Tap eingehängt.
"""
from __future__ import annotations

import random
from datetime import datetime

from menu import GAENGE, load_menu

_GARWORTE = ["blutig", "medium", "durch", "rosa"]
_NOTIZEN = [
    "ohne Zwiebeln", "extra Zaziki", "Sauce separat", "gut durch bitte",
    "ohne Knoblauch", "Pommes statt Reis", "glutenfrei", "wenig Salz",
    "TORA FERTIG MACHEN", "rote bete",
]
_BEILAGEN = ["REIS", "POMMES FRITES", "FOLIENKARTOFFEL", "KETCHUP", "ZAZIKI KLEIN"]

_GANG_MARKER = {"Vorspeise": "*** VORSPEISE ***", "Hauptgang": "HAUPTSPEISE",
                "Dessert": "*** NACHSPEISE ***"}


def _dishes_by_gang():
    by_gang: dict[str, list] = {g: [] for g in GAENGE}
    for candidates in load_menu().values():
        for dish in candidates:
            by_gang[dish.gang].append(dish)
    return by_gang


def _preis(rng: random.Random) -> str:
    euro = rng.randint(3, 28)
    cent = rng.choice(["50", "90", "00"])
    return f"*{euro},{cent}"


def generate_bon(*, tisch: int | None = None, jetzt: datetime | None = None,
                 rng: random.Random | None = None) -> str:
    rng = rng or random
    jetzt = jetzt or datetime.now()
    tisch = tisch if tisch is not None else rng.randint(1, 40)
    by_gang = _dishes_by_gang()

    zeilen = [
        "#0004",
        f"{jetzt.strftime('%d.%m.%Y')}        {jetzt.strftime('%H:%M')}",
        f"Tisch {tisch}",
    ]

    def add_dish(dish):
        menge = rng.choices([1, 2, 3], weights=[7, 2, 1])[0]
        zeilen.append(f"{menge}  {dish.nr} {dish.name.upper()}        {_preis(rng)}")
        if dish.garstufe:
            zeilen.append(f"   {rng.choice(_GARWORTE).upper()}")
        elif rng.random() < 0.15:
            zeilen.append(f"   {rng.choice(_NOTIZEN)}")

    # ~45 % mit Vorspeise (mit Gang-Marker)
    if by_gang["Vorspeise"] and rng.random() < 0.45:
        zeilen.append(_GANG_MARKER["Vorspeise"])
        for dish in rng.sample(by_gang["Vorspeise"],
                               k=rng.randint(1, min(2, len(by_gang["Vorspeise"])))):
            add_dish(dish)

    # Hauptgänge
    for dish in rng.sample(by_gang["Hauptgang"],
                           k=rng.randint(1, min(3, len(by_gang["Hauptgang"])))):
        add_dish(dish)
    if rng.random() < 0.3:
        zeilen.append(f"1  {rng.choice(_BEILAGEN)}")

    # ~20 % Dessert
    if by_gang["Dessert"] and rng.random() < 0.2:
        add_dish(rng.choice(by_gang["Dessert"]))

    zeilen.append("K 4")
    return "\n".join(zeilen)
