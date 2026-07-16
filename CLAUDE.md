# CLAUDE.md

**Bevor du hier arbeitest, lies und befolge [`AGENTS.md`](AGENTS.md)** — die
verbindliche Arbeits-Charta (Zonen 🟢/🟡/🔴, Loop-Protokoll, Datenschutz).

Kern in einem Satz: Agenten treiben das Projekt autonom in kleinen, verifizierten,
reversiblen Schritten voran und eskalieren **nur**, was ohne Tomi nicht geschehen
darf (echte Daten/Kasse, Egress, Go-Live, Geld, Mitarbeiterbezug — siehe §1/§3).

## Projekt
Lokales, selbstlernendes Küchendisplay (KDS) für „Haus Beck", Moers. V1: Screen 1
gegen einen Bon-Simulator. Details: [`README.md`](README.md).

## Befehle
```bash
# Backend (Python/FastAPI)
cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
uvicorn app:app --reload --port 8000        # KDS_AUTOSIM_SEK=8 für Auto-Bons
pytest -q                                    # Testsuite

# Frontend (React/Vite)
cd frontend && npm install && npm run build  # Build -> vom Backend ausgeliefert
npm run dev                                  # Dev-Server :5173 (proxyt /ws & /dev)
npm test                                     # Vitest (Ampel-/Komponenten-Logik)
```

## Definition of Done (jede Iteration)
`pytest` grün · bei Frontend-Änderungen `npm test` grün · betroffener Ablauf
end-to-end beobachtet · kein neues Datenschutz-Risiko (AGENTS.md §3) · kleine,
reversible, committete Änderung.

## Wichtig
- Nur auf dem Arbeitsbranch committen/pushen; **keine PRs ohne Aufforderung**.
- `kds.db`, Rohdaten, `.venv`, `node_modules` bleiben aus dem Git (`.gitignore`).
- Kein externer Netzwerkzugriff im Produktivcode ohne 🔴-Freigabe.
