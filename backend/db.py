"""SQLite Ereignis-Log (Handoff §4).

Das Live-Display ist "der aktuelle Zustand", das Lernen ist "lies die Historie"
— dieselben Daten, zwei Sichten (Handoff §1). Jeder Statuswechsel ist genau
eine Zeile in `events` mit Zeitstempel. Der Rohbon bleibt unveraendert in
`tickets.roh_bon_text` erhalten, damit ein verbesserter Parser spaeter neu
parsen kann.
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Standard-DB auf dem Pi; per KDS_DB_PATH überschreibbar (Tests, mehrere Instanzen).
DEFAULT_DB = os.environ.get(
    "KDS_DB_PATH", str(Path(__file__).resolve().parent / "kds.db"))

EVENT_TYPEN = {"boniert", "gang_gestartet", "item_fertig", "serviert", "zurueckgeholt"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    tisch         TEXT NOT NULL,
    bon_uhrzeit   TEXT,
    roh_bon_text  TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id  INTEGER NOT NULL REFERENCES tickets(id),
    nr         INTEGER,
    name       TEXT NOT NULL,
    menge      INTEGER NOT NULL DEFAULT 1,
    station    TEXT,
    gang       TEXT NOT NULL,
    garstufe   TEXT,
    notiz      TEXT,
    raw_line   TEXT,
    prep_seed_min INTEGER,
    ambiguous  INTEGER NOT NULL DEFAULT 0,
    unbekannt  INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    bezug_typ   TEXT NOT NULL,        -- 'ticket' | 'item'
    bezug_id    INTEGER NOT NULL,
    typ         TEXT NOT NULL,        -- siehe EVENT_TYPEN
    gang        TEXT,                 -- fuer gang_gestartet: welche Gruppe
    zeitstempel TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_items_ticket ON items(ticket_id);
CREATE INDEX IF NOT EXISTS idx_events_bezug ON events(bezug_typ, bezug_id);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path or DEFAULT_DB), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def insert_ticket(conn: sqlite3.Connection, tisch: str, bon_uhrzeit: Optional[str],
                  roh_bon_text: str, created_at: Optional[str] = None) -> int:
    cur = conn.execute(
        "INSERT INTO tickets (tisch, bon_uhrzeit, roh_bon_text, created_at) "
        "VALUES (?, ?, ?, ?)",
        (tisch, bon_uhrzeit, roh_bon_text, created_at or now_iso()),
    )
    conn.commit()
    return int(cur.lastrowid)


def insert_item(conn: sqlite3.Connection, ticket_id: int, *, nr, name, menge,
                station, gang, garstufe, notiz, raw_line, prep_seed_min,
                ambiguous=False, unbekannt=False) -> int:
    cur = conn.execute(
        "INSERT INTO items (ticket_id, nr, name, menge, station, gang, garstufe, "
        "notiz, raw_line, prep_seed_min, ambiguous, unbekannt) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (ticket_id, nr, name, menge, station, gang, garstufe, notiz, raw_line,
         prep_seed_min, int(ambiguous), int(unbekannt)),
    )
    conn.commit()
    return int(cur.lastrowid)


def log_event(conn: sqlite3.Connection, bezug_typ: str, bezug_id: int, typ: str,
              gang: Optional[str] = None, zeitstempel: Optional[str] = None) -> int:
    if typ not in EVENT_TYPEN:
        raise ValueError(f"Unbekannter Event-Typ: {typ}")
    if bezug_typ not in ("ticket", "item"):
        raise ValueError(f"Unbekannter bezug_typ: {bezug_typ}")
    cur = conn.execute(
        "INSERT INTO events (bezug_typ, bezug_id, typ, gang, zeitstempel) "
        "VALUES (?, ?, ?, ?, ?)",
        (bezug_typ, bezug_id, typ, gang, zeitstempel or now_iso()),
    )
    conn.commit()
    return int(cur.lastrowid)


def items_for_ticket(conn: sqlite3.Connection, ticket_id: int) -> list[sqlite3.Row]:
    return list(conn.execute(
        "SELECT * FROM items WHERE ticket_id = ? ORDER BY id", (ticket_id,)))


def events_for(conn: sqlite3.Connection, bezug_typ: str, bezug_id: int) -> list[sqlite3.Row]:
    return list(conn.execute(
        "SELECT * FROM events WHERE bezug_typ = ? AND bezug_id = ? ORDER BY id",
        (bezug_typ, bezug_id)))
