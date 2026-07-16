"""Anonymer Lern-Export + Rohdaten-Löschung (Datenschutz-Entscheidung des Betreibers).

Modell: Der Pi ist ein anonymer Sammler. Täglich werden die **gemessenen
Zubereitungszeiten pro Gericht** (anonym, ohne Tisch/Notiz/Person) als Export
bereitgestellt und anschließend **alle personenbezogenen Rohdaten gelöscht**.

Warum das datenschutzsicher ist:
- Der Export enthält NUR: Artikelnummer, Gerichtname (Stammdaten), Tageszeit-Klasse,
  Anzahl Messungen, Median-Dauer. Kein Tisch, keine Notiz/Allergie, keine Person,
  kein Mitarbeiterbezug (aggregiert pro Gericht, nicht pro Schicht/Person).
- Rohbons, Notizen und der Ereignis-Log werden gelöscht (Datensparsamkeit).
Siehe AGENTS.md §3.
"""
from __future__ import annotations

import json
import statistics
from datetime import datetime
from pathlib import Path

import db


def _tageszeit(ticket) -> str:
    """Lokale Tageszeit-Klasse aus der Bon-Uhrzeit (HH:MM, lokal); Fallback created_at."""
    hhmm = ticket["bon_uhrzeit"]
    if hhmm and ":" in hhmm:
        try:
            h = int(hhmm.split(":")[0])
        except ValueError:
            h = 0
    else:
        h = datetime.fromisoformat(ticket["created_at"]).hour
    if 11 <= h < 15:
        return "mittag"
    if 17 <= h < 23:
        return "abend"
    return "rand"


def _erste_dauer_sek(conn, ticket_id: int, item) -> float | None:
    """Gemessene Zeit start->fertig für die erste Fertigstellung des Items (Sek.)."""
    fertig = None
    for ev in db.events_for(conn, "item", item["id"]):
        if ev["typ"] == "item_fertig":
            fertig = ev["zeitstempel"]
            break
    if fertig is None:
        return None
    start = None
    for ev in db.events_for(conn, "ticket", ticket_id):
        if (ev["typ"] == "gang_gestartet" and ev["gang"] == item["gang"]
                and ev["zeitstempel"] <= fertig):
            start = ev["zeitstempel"]  # spätestes passendes gewinnt
    if start is None:
        return None
    dauer = (datetime.fromisoformat(fertig) - datetime.fromisoformat(start)).total_seconds()
    return dauer if dauer >= 0 else None


def sammle_lernzeiten(conn, cutoff_iso: str) -> list[dict]:
    """Anonyme, gemessene Zeiten je (Gericht, Tageszeit) für Tickets VOR cutoff_iso."""
    tickets = conn.execute(
        "SELECT * FROM tickets WHERE created_at < ?", (cutoff_iso,)).fetchall()
    roh: dict[tuple, dict] = {}
    for t in tickets:
        tz = _tageszeit(t)
        for it in db.items_for_ticket(conn, t["id"]):
            dauer = _erste_dauer_sek(conn, t["id"], it)
            if dauer is None:
                continue
            eintrag = roh.setdefault((it["nr"], tz), {"name": it["name"], "dauern": []})
            eintrag["dauern"].append(dauer)

    out = []
    for (nr, tz), d in sorted(roh.items(), key=lambda x: (x[0][0] or 0, x[0][1])):
        median = round(statistics.median(d["dauern"]))
        out.append({
            "nr": nr,
            "name": d["name"],
            "tageszeit": tz,
            "anzahl": len(d["dauern"]),
            "median_sek": median,
            "median_min": round(median / 60, 1),
        })
    return out


def schreibe_export(daten: list[dict], ordner: str, stempel_iso: str) -> str:
    Path(ordner).mkdir(parents=True, exist_ok=True)
    pfad = Path(ordner) / f"lernzeiten-{stempel_iso[:10]}.json"
    pfad.write_text(json.dumps({
        "erstellt": stempel_iso,
        "hinweis": ("Anonym: nur Gericht -> gemessene Zubereitungszeiten. "
                    "Keine personenbezogenen Daten, kein Mitarbeiterbezug."),
        "zeiten": daten,
    }, ensure_ascii=False, indent=2))
    return str(pfad)


def purge_rohdaten(conn, cutoff_iso: str) -> int:
    """Löscht tickets/items/events für Tickets VOR cutoff_iso. Gibt Anzahl gelöschter
    Tickets zurück. Anonyme Exporte liegen zu diesem Zeitpunkt bereits als Datei vor."""
    ids = [r["id"] for r in conn.execute(
        "SELECT id FROM tickets WHERE created_at < ?", (cutoff_iso,))]
    if not ids:
        return 0
    q = ",".join("?" * len(ids))
    item_ids = [r["id"] for r in conn.execute(
        f"SELECT id FROM items WHERE ticket_id IN ({q})", ids)]
    if item_ids:
        iq = ",".join("?" * len(item_ids))
        conn.execute(f"DELETE FROM events WHERE bezug_typ='item' AND bezug_id IN ({iq})",
                     item_ids)
    conn.execute(f"DELETE FROM events WHERE bezug_typ='ticket' AND bezug_id IN ({q})", ids)
    conn.execute(f"DELETE FROM items WHERE ticket_id IN ({q})", ids)
    conn.execute(f"DELETE FROM tickets WHERE id IN ({q})", ids)
    conn.commit()
    return len(ids)


def _heute_beginn_iso(jetzt_iso: str) -> str:
    """00:00 des heutigen Tages -> Cutoff: gestern & älter werden verarbeitet/gelöscht."""
    return jetzt_iso[:10] + "T00:00:00+00:00"


def taeglicher_lauf(conn, jetzt_iso: str, export_ordner: str,
                    cutoff_iso: str | None = None) -> dict:
    """Anonyme Zeiten exportieren, DANN Rohdaten vor dem Cutoff löschen."""
    cutoff = cutoff_iso or _heute_beginn_iso(jetzt_iso)
    daten = sammle_lernzeiten(conn, cutoff)
    pfad = schreibe_export(daten, export_ordner, jetzt_iso)
    geloescht = purge_rohdaten(conn, cutoff)
    return {"export": pfad, "zeiten": len(daten), "geloeschte_tickets": geloescht}
