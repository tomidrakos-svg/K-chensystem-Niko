"""KDS-Kernlogik: Bon aufnehmen, Gang-Logik, Ampel-Zustand, Live-Projektion.

Event-Sourcing (Handoff §1/§4): jeder Zustand wird aus dem Ereignis-Log
abgeleitet. `snapshot()` liest Tickets/Items/Events aus SQLite und projiziert
den aktuellen Zustand — dieselben Daten, die das spaetere Lernen auswertet.
"""
from __future__ import annotations

import sqlite3
from typing import Optional

import config
import db
from menu import GAENGE, resolve
from parser import parse_bon

# Reihenfolge der Gaenge in der Anzeige.
_GANG_ORDER = {g: i for i, g in enumerate(GAENGE)}


class KDSService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---------- Bon-Aufnahme ----------
    def ingest_bon(self, roh_text: str) -> int:
        parsed = parse_bon(roh_text)
        ticket_id = db.insert_ticket(
            self.conn, tisch=parsed.tisch, bon_uhrzeit=parsed.uhrzeit,
            roh_bon_text=parsed.roh_text,
        )
        gaenge_present: set[str] = set()
        for pi in parsed.items:
            res = resolve(pi.nr, pi.name)
            dish = res.dish
            # Unbekannte nr bleibt sichtbar und laeuft als Hauptgang mit.
            gang = dish.gang if dish else "Hauptgang"
            db.insert_item(
                self.conn, ticket_id,
                nr=pi.nr,
                name=dish.name if dish else pi.name,
                menge=pi.menge,
                station=dish.station if dish else None,
                gang=gang,
                garstufe=pi.garstufe,
                notiz=pi.notiz,
                raw_line=pi.raw_line,
                prep_seed_min=dish.prep_seed_min if dish else 10,
                ambiguous=res.ambiguous,
                unbekannt=res.unknown or pi.unparsbar,
            )
            gaenge_present.add(gang)

        db.log_event(self.conn, "ticket", ticket_id, "boniert")

        # Gang-Logik (Handoff §5): Vorspeise startet sofort.
        if "Vorspeise" in gaenge_present:
            db.log_event(self.conn, "ticket", ticket_id, "gang_gestartet",
                         gang="Vorspeise")
        else:
            # Kein Vorspeise -> Hauptgang startet sofort.
            if "Hauptgang" in gaenge_present:
                db.log_event(self.conn, "ticket", ticket_id, "gang_gestartet",
                             gang="Hauptgang")
            if "Dessert" in gaenge_present:
                db.log_event(self.conn, "ticket", ticket_id, "gang_gestartet",
                             gang="Dessert")
        return ticket_id

    # ---------- Aktionen ----------
    def hauptgang_start(self, ticket_id: int) -> None:
        """Der einzige farbige Button: startet Hauptgang (und Dessert) eines Tickets."""
        started = self._started_gaenge(ticket_id)
        present = self._gaenge_present(ticket_id)
        for gang in ("Hauptgang", "Dessert"):
            if gang in present and gang not in started:
                db.log_event(self.conn, "ticket", ticket_id, "gang_gestartet",
                             gang=gang)

    def item_fertig(self, item_id: int) -> None:
        row = self.conn.execute(
            "SELECT ticket_id, gang FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            return
        ticket_id, gang = row["ticket_id"], row["gang"]
        # Nur erledigbar, wenn der Gang gestartet ist (geparkte Items sind gesperrt).
        if gang not in self._started_gaenge(ticket_id):
            return
        if self._item_ist_fertig(item_id):
            return
        db.log_event(self.conn, "item", item_id, "item_fertig", gang=gang)
        if self._alle_items_fertig(ticket_id):
            db.log_event(self.conn, "ticket", ticket_id, "serviert")

    def zurueckholen(self, ticket_id: int) -> None:
        if self._ticket_status(ticket_id) == "serviert":
            db.log_event(self.conn, "ticket", ticket_id, "zurueckgeholt")

    # ---------- Projektion ----------
    def snapshot(self) -> dict:
        tickets = list(self.conn.execute("SELECT * FROM tickets ORDER BY id"))
        aktiv, recall = [], []
        for t in tickets:
            status = self._ticket_status(t["id"])
            view = self._ticket_view(t)
            if status == "serviert":
                recall.append(view)
            else:
                aktiv.append(view)
        recall = recall[-config.RECALL_MAX:][::-1]  # neueste zuerst
        return {
            "type": "snapshot",
            "server_now": db.now_iso(),
            "config": config.ampel_config(),
            "tickets": aktiv,          # aelteste zuerst (oben links)
            "recall": recall,
        }

    # ---------- interne Helfer ----------
    def _ticket_events(self, ticket_id: int) -> list[sqlite3.Row]:
        return db.events_for(self.conn, "ticket", ticket_id)

    def _ticket_status(self, ticket_id: int) -> str:
        """Letzter ticket-bezogener Zustand: boniert | serviert | zurueckgeholt."""
        last = None
        for ev in self._ticket_events(ticket_id):
            if ev["typ"] in ("serviert", "zurueckgeholt", "boniert"):
                last = ev["typ"]
        return last or "boniert"

    def _gaenge_present(self, ticket_id: int) -> set[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT gang FROM items WHERE ticket_id = ?", (ticket_id,))
        return {r["gang"] for r in rows}

    def _started_gaenge(self, ticket_id: int) -> dict[str, str]:
        """gang -> Startzeitstempel (letztes gang_gestartet gewinnt)."""
        started: dict[str, str] = {}
        for ev in self._ticket_events(ticket_id):
            if ev["typ"] == "gang_gestartet" and ev["gang"]:
                started[ev["gang"]] = ev["zeitstempel"]
        return started

    def _item_ist_fertig(self, item_id: int) -> bool:
        return any(ev["typ"] == "item_fertig"
                   for ev in db.events_for(self.conn, "item", item_id))

    def _alle_items_fertig(self, ticket_id: int) -> bool:
        items = db.items_for_ticket(self.conn, ticket_id)
        return bool(items) and all(self._item_ist_fertig(i["id"]) for i in items)

    def _ticket_view(self, t: sqlite3.Row) -> dict:
        items = db.items_for_ticket(self.conn, t["id"])
        started = self._started_gaenge(t["id"])

        gaenge: dict[str, dict] = {}
        for it in items:
            g = gaenge.setdefault(it["gang"], {
                "gang": it["gang"], "items": [], "erwartet_min": 0,
                "gestartet_at": started.get(it["gang"]),
            })
            fertig = self._item_ist_fertig(it["id"])
            g["items"].append({
                "id": it["id"],
                "nr": it["nr"],
                "name": it["name"],
                "menge": it["menge"],
                "station": it["station"],
                "garstufe": it["garstufe"],
                "notiz": it["notiz"],
                "raw_line": it["raw_line"],
                "gang": it["gang"],
                "fertig": fertig,
                "ambiguous": bool(it["ambiguous"]),
                "unbekannt": bool(it["unbekannt"]),
            })
            g["erwartet_min"] = max(g["erwartet_min"], it["prep_seed_min"] or 0)

        gang_list = []
        for name, g in gaenge.items():
            alle_fertig = all(i["fertig"] for i in g["items"])
            if g["gestartet_at"] is None:
                status = "geparkt"
            elif alle_fertig:
                status = "fertig"
            else:
                status = "laufend"
            g["status"] = status
            gang_list.append(g)
        gang_list.sort(key=lambda g: _GANG_ORDER.get(g["gang"], 99))

        return {
            "id": t["id"],
            "tisch": t["tisch"],
            "bon_uhrzeit": t["bon_uhrzeit"],
            "created_at": t["created_at"],
            "gaenge": gang_list,
        }
