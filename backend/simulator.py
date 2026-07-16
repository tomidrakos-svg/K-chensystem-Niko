"""Bon-Simulator (Handoff §9.2 / §12.2).

Erzeugt plausible Kuechenbons im Parser-Format. Ersetzt in V1 die Demo-Steuerung
"＋ Bon" aus dem Mockup; die reale Kassen-/Drucker-Quelle wird spaeter hinter
`bonsource.PrinterTcpSource` eingehaengt, ohne dass sich Service/UI aendern.
"""
from __future__ import annotations

import random
from datetime import datetime

from menu import GAENGE, load_menu

_GARWORTE = ["blutig", "medium", "durch", "rosa"]
_NOTIZEN = [
    "ohne Zwiebeln", "extra Zaziki", "Sauce separat", "gut durch bitte",
    "ohne Knoblauch", "Pommes statt Reis", "glutenfrei", "wenig Salz",
]


def _dishes_by_gang():
    by_gang: dict[str, list] = {g: [] for g in GAENGE}
    for candidates in load_menu().values():
        for dish in candidates:
            by_gang[dish.gang].append(dish)
    return by_gang


def generate_bon(*, tisch: int | None = None, jetzt: datetime | None = None,
                 rng: random.Random | None = None) -> str:
    """Baut einen zufaelligen Bon-Rohtext."""
    rng = rng or random
    jetzt = jetzt or datetime.now()
    tisch = tisch if tisch is not None else rng.randint(1, 40)
    by_gang = _dishes_by_gang()

    zeilen = [f"TISCH {tisch}    {jetzt.strftime('%H:%M')}", "-" * 24]

    def add_dish(dish):
        menge = rng.choices([1, 2, 3], weights=[7, 2, 1])[0]
        zeilen.append(f"{menge}x  {dish.nr}  {dish.name}")
        if dish.garstufe:
            zeilen.append(f"    >> {rng.choice(_GARWORTE)}")
        elif rng.random() < 0.15:
            zeilen.append(f"    >> {rng.choice(_NOTIZEN)}")

    # ~45 % der Tische haben eine Vorspeise.
    if by_gang["Vorspeise"] and rng.random() < 0.45:
        for dish in rng.sample(by_gang["Vorspeise"],
                               k=rng.randint(1, min(2, len(by_gang["Vorspeise"])))):
            add_dish(dish)

    # 1-3 Hauptgaenge.
    for dish in rng.sample(by_gang["Hauptgang"],
                           k=rng.randint(1, min(3, len(by_gang["Hauptgang"])))):
        add_dish(dish)

    # ~20 % haben ein Dessert.
    if by_gang["Dessert"] and rng.random() < 0.2:
        add_dish(rng.choice(by_gang["Dessert"]))

    zeilen.append("-" * 24)
    return "\n".join(zeilen)
