# Küchendisplay (KDS) — Haus Beck

Ein lokal laufendes, selbstlernendes Küchendisplay: liest Bestellungen live,
zeigt Wartezeit pro Tisch und Gang und protokolliert jeden Statuswechsel als
Ereignis (damit das spätere Selbstlernen „abfällt"). **Local-first** — alles
läuft auf einem Raspberry Pi, das iPad ist nur ein Browser-Kiosk.

Dies ist **V1** gemäß Handoff §9: Screen 1 (Küche), Bon-Parser gegen einen
Simulator, Datenmodell + Event-Log, Gang-Logik, Ampel und die Zurückholen-Ablage.
Nicht in V1: Lern-Schicht, Screen 2/3, zweite Station, Cloud, Kassen-API.

## Architektur

```
Kasse/Drucker ──(später)──▶ BonSource ──▶ Parser ──▶ Service (SQLite Event-Log)
                              (V1: Simulator)                         │
                                                                       ▼
                              iPad-Kiosk ◀── WebSocket (Live-Snapshot) App
```

- **backend/** — Python (FastAPI + uvicorn + sqlite3). Nimmt Bons an, führt die
  Gang-/Ampel-Logik, hält das Ereignis-Log und broadcastet den Zustand per
  WebSocket.
- **frontend/** — React (Vite). Screen 1 nach Handoff §7. Wird gebaut und vom
  Backend statisch ausgeliefert.
- **menu.json** — Stammdaten inkl. abgeleitetem `gang`-Feld (Vorspeise/Hauptgang/
  Dessert).
- **scripts/kiosk/** — systemd-Dienst + Anleitung für Pi & iPad.

### Zentrale Regeln (aus dem Handoff)
- **Gang-Logik (§5):** Vorspeise-Uhr startet sofort. Hauptgang/Dessert sind
  geparkt, bis der Koch **„Hauptgang starten"** tippt (der einzige farbige
  Button). Ohne Vorspeise startet der Hauptgang sofort.
- **Ampel (§6):** eine Uhr pro Gang-Gruppe, erwartete Zeit = `max(prep_seed_min)`.
  neutral → gelb ab 72 % → rot ab 100 %. Schwellen sind **konfigurierbar**
  (`backend/config.py`), nicht hartcodiert. Alternativ **Minuten-Modus**
  (`KDS_AMPEL_MODUS=minuten` mit `KDS_AMPEL_GELB_MIN`/`KDS_AMPEL_ROT_MIN`) —
  feste Minuten-Schwellen statt Prozent.
- **Nie blind (§2):** unbekannte `nr` oder unparsbare Zeilen werden trotzdem als
  Rohtext angezeigt und markiert; ein kaputter Bon stoppt nie den Betrieb.
- **Ehrliches Logbuch (§1/§4):** jeder Zustand ist aus `events` abgeleitet
  (Event-Sourcing); der Rohbon bleibt für späteres Reparsen erhalten.

## Lokal starten (Entwicklung)

```bash
# Backend
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000          # optional: KDS_AUTOSIM_SEK=8 für Auto-Bons

# Frontend (zweites Terminal)
cd frontend
npm install
npm run dev                                    # Vite auf :5173, proxyt /ws & /dev ans Backend
```

Display: <http://localhost:5173> (Dev) bzw. <http://localhost:8000> nach
`npm run build` (Backend serviert dann den Build selbst).

Bon manuell einspeisen (ersetzt das Mockup-„＋ Bon"):
```bash
curl -X POST localhost:8000/dev/bon                       # zufälliger Sim-Bon
curl -X POST localhost:8000/dev/bon/custom --data-binary $'TISCH 7 19:00\n1x 27 Huehnersuppe\n2x 1 Gyros\n'
```

## Tests & Verifikation

```bash
cd backend && . .venv/bin/activate && pytest -q       # Parser, Menü/Kollisionen, Gang, Ampel, WS
```

Der End-to-End-Flow (Bon → Gang-Gruppen → Hauptgang starten → Tap-to-done →
Recall) wurde zusätzlich im Browser gegen den laufenden Server verifiziert.

## Datenmodell (SQLite, Event-Log)

- `tickets` — id, tisch, bon_uhrzeit, **roh_bon_text**, created_at
- `items` — id, ticket_id, nr, name, menge, station, gang, garstufe, notiz,
  raw_line, prep_seed_min, ambiguous, unbekannt
- `events` — id, bezug_typ, bezug_id, **typ**, gang, zeitstempel
  mit `typ ∈ {boniert, gang_gestartet, item_fertig, serviert, zurueckgeholt}`

Das spätere Selbstlernen (nicht in V1) liest denselben Log: echte Zeit pro
Gericht = `gang_gestartet → item_fertig`, Median/Perzentil überschreibt
`prep_seed_min`.

## Reale Kassen-/Drucker-Anbindung

Bewusst noch offen und hinter `backend/bonsource.py::PrinterTcpSource` gekapselt.
Anschluss-Optionen und die wichtige Korrektur zum „passiven Mithören" stehen in
[`scripts/kiosk/README.md`](scripts/kiosk/README.md).
