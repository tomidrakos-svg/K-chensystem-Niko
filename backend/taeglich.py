"""CLI: täglicher anonymer Lern-Export + Rohdaten-Löschung.

Wird per systemd-Timer um 11:00 aufgerufen (siehe scripts/kiosk/). Schreibt die
anonymen Zeiten in den Export-Ordner und löscht anschließend alle
personenbezogenen Rohdaten des Vortags und älter. Siehe AGENTS.md §3 / lernexport.py.
"""
from __future__ import annotations

import os
from pathlib import Path

import db
import lernexport as lx

EXPORT_DIR = os.environ.get(
    "KDS_EXPORT_DIR", str(Path(__file__).resolve().parent / "exports"))


def main() -> None:
    conn = db.connect()
    res = lx.taeglicher_lauf(conn, db.now_iso(), EXPORT_DIR)
    print(f"[taeglich] Export: {res['export']} | Zeiten-Eintraege: {res['zeiten']} | "
          f"geloeschte Tickets: {res['geloeschte_tickets']}")


if __name__ == "__main__":
    main()
