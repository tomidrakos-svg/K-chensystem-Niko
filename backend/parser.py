"""Bon-Parser (Handoff §3).

Das exakte Textformat der Kasse ist noch unbekannt (wird per Bon-Foto geeicht,
Handoff §10). Bis dahin arbeiten wir gegen ein bewusst einfaches, hier
dokumentiertes Format, das der Simulator erzeugt. Der Parser ist TOLERANT:
eine unbekannte Artikelnummer oder eine nicht parsbare Zeile stoppt nie den
Betrieb — sie wird als Rohzeile mitgefuehrt und markiert ("nie blind", §1/§2).

Erwartetes Format (Platzhalter bis zur Eichung)::

    TISCH 12        18:42
    ------------------------
    2x  1   Gyros
    1x  76  3 Rindermedaillons Pfeffer
        >> medium
    1x  139 Pommes frites
        >> ohne Zwiebeln
    ------------------------

- Kopfzeile: ``TISCH <nr>   <HH:MM>``
- Artikelzeile: ``<menge>x  <nr>  <name>``
- Folgezeile ``>> ...``: Garstufe (wenn Garwort) sonst Notiz, gehoert zum
  vorigen Artikel.
- Trenn-/Leerzeilen werden ignoriert; alles andere wird als Rohzeile behalten.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# Bekannte Garstufen (fuer >> Zeilen). Alles andere unter >> ist eine Notiz.
GARSTUFEN = {
    "blutig", "rare", "englisch", "medium rare", "medium", "rosa",
    "halbdurch", "durch", "well done", "welldone", "durchgebraten",
}

_HEADER_RE = re.compile(r"^\s*TISCH\s+(\S+)\s+(\d{1,2}:\d{2})\s*$", re.IGNORECASE)
_ITEM_RE = re.compile(r"^\s*(\d+)\s*[xX]\s+(\d+)\s+(.+?)\s*$")
_NOTE_RE = re.compile(r"^\s*>>\s*(.+?)\s*$")
_SEPARATOR_RE = re.compile(r"^[\s\-=_*]*$")


@dataclass
class ParsedItem:
    menge: int
    nr: Optional[int]
    name: str
    garstufe: Optional[str] = None
    notiz: Optional[str] = None
    raw_line: str = ""
    unparsbar: bool = False   # Zeile passte auf kein Muster


@dataclass
class ParsedBon:
    tisch: str
    uhrzeit: Optional[str]
    roh_text: str
    items: list[ParsedItem] = field(default_factory=list)


def _classify_note(text: str) -> tuple[Optional[str], Optional[str]]:
    """Gibt (garstufe, notiz) zurueck — genau eines ist gesetzt."""
    if text.strip().lower() in GARSTUFEN:
        return text.strip(), None
    return None, text.strip()


def parse_bon(raw_text: str) -> ParsedBon:
    lines = raw_text.splitlines()
    tisch = "?"
    uhrzeit: Optional[str] = None
    items: list[ParsedItem] = []

    for line in lines:
        if _SEPARATOR_RE.match(line):
            continue

        header = _HEADER_RE.match(line)
        if header:
            tisch = header.group(1)
            uhrzeit = header.group(2)
            continue

        note = _NOTE_RE.match(line)
        if note:
            garstufe, notiz = _classify_note(note.group(1))
            if items:
                # An den letzten Artikel anhaengen.
                if garstufe:
                    items[-1].garstufe = garstufe
                if notiz:
                    items[-1].notiz = (
                        f"{items[-1].notiz}; {notiz}" if items[-1].notiz else notiz
                    )
            else:
                # >> ohne vorigen Artikel: als eigenstaendige Rohzeile behalten.
                items.append(ParsedItem(menge=1, nr=None, name=note.group(1),
                                        raw_line=line, unparsbar=True))
            continue

        item = _ITEM_RE.match(line)
        if item:
            items.append(ParsedItem(
                menge=int(item.group(1)),
                nr=int(item.group(2)),
                name=item.group(3).strip(),
                raw_line=line,
            ))
            continue

        # Nichts hat gepasst: Zeile nicht verwerfen, sondern roh behalten.
        items.append(ParsedItem(menge=1, nr=None, name=line.strip(),
                                raw_line=line, unparsbar=True))

    return ParsedBon(tisch=tisch, uhrzeit=uhrzeit, roh_text=raw_text, items=items)
