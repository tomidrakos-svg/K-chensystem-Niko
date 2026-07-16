"""Zentrale, betrieblich anpassbare Stellschrauben.

Recherche-Erkenntnis: etablierte KDS (Fresh KDS) legen die Farb-Schwellen
bewusst KONFIGURIERBAR aus, nicht als hartcodierte Sekundenwerte. Darum stehen
die Ampel-Schwellen hier zentral und nicht im Code verstreut. Default nach
Handoff §6: gelb ab ~72 %, rot ab 100 % der erwarteten Gang-Zeit.
"""
from __future__ import annotations

import os

# Ampel-Modus: "prozent" (Anteil der erwarteten Gang-Zeit) oder "minuten"
# (feste Minuten-Schwellen, unabhaengig vom Gericht — manche Koeche denken so).
AMPEL_MODUS = os.environ.get("KDS_AMPEL_MODUS", "prozent")

# Prozent-Modus: Anteil der erwarteten Gang-Zeit (max prep_seed_min der Gruppe).
AMPEL_GELB_PCT = float(os.environ.get("KDS_AMPEL_GELB_PCT", "0.72"))
AMPEL_ROT_PCT = float(os.environ.get("KDS_AMPEL_ROT_PCT", "1.00"))

# Minuten-Modus: absolute Schwellen in Minuten seit Gang-Start.
AMPEL_GELB_MIN = float(os.environ.get("KDS_AMPEL_GELB_MIN", "8"))
AMPEL_ROT_MIN = float(os.environ.get("KDS_AMPEL_ROT_MIN", "12"))

# Wie viele abgeschlossene Tickets die Zurueckholen-Ablage vorhaelt (Handoff §7).
RECALL_MAX = int(os.environ.get("KDS_RECALL_MAX", "6"))

# Optionales automatisches Erzeugen von Sim-Bons (Sekunden; 0 = aus).
AUTOSIM_INTERVALL_SEK = float(os.environ.get("KDS_AUTOSIM_SEK", "0"))


def ampel_config() -> dict:
    return {
        "modus": AMPEL_MODUS,
        "gelb_pct": AMPEL_GELB_PCT,
        "rot_pct": AMPEL_ROT_PCT,
        "gelb_min": AMPEL_GELB_MIN,
        "rot_min": AMPEL_ROT_MIN,
    }
