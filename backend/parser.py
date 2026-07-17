"""Bon-Parser (Handoff §3) — geeicht am echten Schultes-Küchenbon.

Format aus echten Bons (Kasse: Schultes S-700 flextouch+, Küchendrucker seriell)::

    #0004
    17.07.2026            13:25
    Tisch 41
    *** VORSPEISE ***                  ← Gang-Marker (optional, wird erkannt/übersprungen)
    1  4 GYROS ÜBERBACKEN       *13,90  ← <menge>  <nr> <NAME>   *<preis>
       TORA FERTIG MACHEN               ← Notiz / Sonderwunsch (eigene Zeile)
    1  10 BIFTEKI              *13,90
       MEDIUM                           ← Garstufe (eigene Zeile)
    1  REIS                             ← Beilage/Extra, teils ohne Nr
    K 4                                 ← Küchen-Station

Der Parser bleibt TOLERANT (Handoff §1/§2 „nie blind"): unbekannte Nummern und
nicht zuordenbare Zeilen stoppen nie den Betrieb. Er versteht zusätzlich das alte
Simulator-Format (`2x  1  Gyros`, `>> medium`), damit nichts regressiert. Preise
werden ignoriert; Gang-Marker werden erkannt und übersprungen (die Gang-Zuordnung
kommt weiterhin aus menu.json — bis der rohe serielle Strom die Marker-Semantik
bestätigt).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

GARSTUFEN = {
    "blutig", "rare", "englisch", "medium rare", "medium", "rosa",
    "halbdurch", "durch", "well done", "welldone", "durchgebraten",
}

# Kopf / Struktur
_TISCH_RE = re.compile(r"tisch\s+(\d+)", re.IGNORECASE)
_TIME_RE = re.compile(r"\b(\d{1,2}:\d{2})\b")
_HEADER_DT_RE = re.compile(r"^\s*(?:\d{1,2}\.\d{1,2}\.\d{2,4})?\s*(?:\d{1,2}:\d{2})?\s*$")
_MARKER_RE = re.compile(
    r"^\s*\*{0,3}\s*(vorspeise[n]?|hauptspeise|hauptgang|hauptgericht|"
    r"nachspeise|nachtisch|dessert)\s*\*{0,3}\s*$", re.IGNORECASE)
_FOOTER_RE = re.compile(r"^\s*(#\s*\d+|k\s*\d+|\*{2,})\s*$", re.IGNORECASE)
_SEPARATOR_RE = re.compile(r"^[\s\-=_]*$")
_PRICE_ONLY_RE = re.compile(r"^\s*\*?\s*\d[\d.]*,\d{2}\s*$")
_TRAIL_PRICE_RE = re.compile(r"\s*\*?\s*\d[\d.]*,\d{2}\s*$")

# Positionen
_ITEM_NR_RE = re.compile(r"^\s*(\d+)\s*[xX]?\s+(\d+)\s+(.+?)\s*$")
_ITEM_NONR_RE = re.compile(r"^\s*(\d+)\s*[xX]?\s+([^\d\s].*?)\s*$")
_NOTE_RE = re.compile(r"^\s*>>\s*(.+?)\s*$")


@dataclass
class ParsedItem:
    menge: int
    nr: Optional[int]
    name: str
    garstufe: Optional[str] = None
    notiz: Optional[str] = None
    raw_line: str = ""
    unparsbar: bool = False


@dataclass
class ParsedBon:
    tisch: str
    uhrzeit: Optional[str]
    roh_text: str
    items: list[ParsedItem] = field(default_factory=list)


def _classify_note(text: str) -> tuple[Optional[str], Optional[str]]:
    """(garstufe, notiz) — genau eines ist gesetzt. Garstufe normalisiert klein."""
    t = text.strip()
    if t.lower() in GARSTUFEN:
        return t.lower(), None
    return None, t


def _anhaengen(items: list[ParsedItem], garstufe, notiz, roh_line: str) -> None:
    """Garstufe/Notiz an den letzten Artikel hängen; ohne Vorgänger als Rohzeile."""
    if not items:
        items.append(ParsedItem(menge=1, nr=None, name=roh_line.strip(),
                                raw_line=roh_line, unparsbar=True))
        return
    if garstufe:
        items[-1].garstufe = garstufe
    if notiz:
        items[-1].notiz = f"{items[-1].notiz}; {notiz}" if items[-1].notiz else notiz


def parse_bon(raw_text: str) -> ParsedBon:
    lines = raw_text.splitlines()
    tisch = "?"
    items: list[ParsedItem] = []

    # Uhrzeit Eingang: einzige HH:MM-Angabe auf dem Bon.
    zeiten = _TIME_RE.findall(raw_text)
    uhrzeit = zeiten[-1] if zeiten else None

    for line in lines:
        if _SEPARATOR_RE.match(line):
            continue
        tisch_m = _TISCH_RE.search(line)
        if tisch_m:
            tisch = tisch_m.group(1)
            continue
        if _MARKER_RE.match(line) or _FOOTER_RE.match(line) or _PRICE_ONLY_RE.match(line):
            continue
        if _HEADER_DT_RE.match(line):   # reine Datum-/Zeit-Kopfzeile
            continue

        note = _NOTE_RE.match(line)     # altes ">> …"-Format
        if note:
            g, n = _classify_note(note.group(1))
            _anhaengen(items, g, n, line)
            continue

        line_np = _TRAIL_PRICE_RE.sub("", line)   # Preis am Zeilenende entfernen
        m = _ITEM_NR_RE.match(line_np)
        if m:
            items.append(ParsedItem(menge=int(m.group(1)), nr=int(m.group(2)),
                                    name=m.group(3).strip(), raw_line=line))
            continue
        m2 = _ITEM_NONR_RE.match(line_np)
        if m2:
            items.append(ParsedItem(menge=int(m2.group(1)), nr=None,
                                    name=m2.group(2).strip(), raw_line=line))
            continue

        # Kein Artikel: Garstufe- oder Notizzeile (gehört zum vorigen Artikel).
        g, n = _classify_note(line)
        _anhaengen(items, g, n, line)

    return ParsedBon(tisch=tisch, uhrzeit=uhrzeit, roh_text=raw_text, items=items)
