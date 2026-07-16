# Projekt-Stand — Küchendisplay Haus Beck

*Stand: 2026-07-16 · Branch `claude/new-session-y9gd07`*

Kompakter Einstieg: was gebaut/verifiziert ist, was noch fehlt, und was du (Tomi)
liefern musst. Details in den verlinkten Dokumenten.

## In einem Satz
Lokales, selbstlernendes iPad-Küchendisplay (KDS) für „Haus Beck", Moers. **V1 ist
gebaut und verifiziert — gegen einen Bon-Simulator**, weil die echte Kasse noch
nicht angebunden ist.

## Status — V1 steht

| Baustein | Stand |
|---|---|
| `menu.json` + abgeleitetes `gang`-Feld | ✅ |
| Bon-Parser (tolerant, „nie blind") + Simulator | ✅ |
| Datenmodell + Ereignis-Log (SQLite, event-sourced) | ✅ |
| Gang-Logik (Vorspeise sofort / Hauptgang geparkt bis Tap) | ✅ |
| Ampel (Prozent- **oder** Minuten-Modus, konfigurierbar) | ✅ |
| Screen 1 (React) nach Goldstandard, Hell/Dunkel | ✅ |
| WebSocket-Live-Updates, Tap-to-done, Zurückholen | ✅ |
| Datenschutz: anonymer Export + tägliche Löschung + LAN-Download | ✅ |
| Reale Kassen-/Drucker-Anbindung | ⛔ blockiert (siehe unten) |
| Screen 2 (All-Day-View), Screen 3, On-Device-Lernen | 🔜 später |

**48 automatisierte Tests grün** (32 Backend/pytest, 16 Frontend/Vitest), Kernabläufe
zusätzlich end-to-end im Browser verifiziert.

## Datenschutz (Kurzfassung)
Local-first. Der Pi ist ein **anonymer Sammler**: täglich 11:00 werden anonyme
Zubereitungszeiten je Gericht exportiert (Download über `…:8000/export`), danach
**alle personenbezogenen Rohdaten gelöscht**. Keine Mitarbeiterüberwachung. Regeln:
`AGENTS.md` §3.

## Blockiert — was du liefern musst
Der nächste *substanzielle* Schritt braucht Input von dir (Details:
`docs/LIEFERCHECKLISTE.md`):
1. **Foto eines echten Küchenbons** → Parser eichen.
2. **Kassen-Marke/-Modell + API ja/nein** → Anbindungsweg wählen.
3. **Echtes `kuechendisplay-mockup.jsx`** → Design final abgleichen.

## Roadmap (sobald die Inputs da sind)
1. Parser am echten Bon eichen; reale `BonSource` einhängen (Anschluss-Option a/b/c
   aus `scripts/kiosk/README.md`).
2. Testbetrieb parallel zum Papier.
3. Screen 2 mit All-Day-View.
4. Screen 3 + Lernen (anonyme Export-Zeiten in `prep_seed_min` zurückspielen).

## Dokumenten-Index
- `README.md` — Überblick, Architektur, lokal starten.
- `AGENTS.md` — Arbeits-Charta für Agenten (Zonen 🟢/🟡/🔴, Orchestrator-Modell, Datenschutz).
- `CLAUDE.md` — Kurz-Anleitung + Befehle + Definition of Done.
- `docs/DESIGN-REFERENZ.md` — recherchierter Goldstandard, alle To-dos abgehakt.
- `docs/LIEFERCHECKLISTE.md` — was du besorgst, damit es live geht.
- `scripts/kiosk/README.md` — Pi/iPad-Setup, Drucker-Anschlussoptionen, täglicher Datenschutz-Lauf.

## Starten / Testen
```bash
# Backend
cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
uvicorn app:app --reload --port 8000        # KDS_AUTOSIM_SEK=8 für Auto-Bons
pytest -q
# Frontend
cd frontend && npm install && npm run build  # bzw. npm run dev
npm test
```
