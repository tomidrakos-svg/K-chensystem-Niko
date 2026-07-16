"""FastAPI-App: statisches Frontend, WebSocket-Live-Updates, Dev-Bon-Eingang.

Local-first (Handoff §1/§2): laeuft komplett auf dem Pi, iPad ist nur ein
Browser-Kiosk. Der Server broadcastet bei jeder Zustandsaenderung einen
vollstaendigen Snapshot an alle verbundenen Displays (robust bei <=15 Tickets).
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import config
import db
from bonsource import SimulatorSource
from service import KDSService

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

conn = db.connect()
service = KDSService(conn)
source = SimulatorSource(intervall_sek=config.AUTOSIM_INTERVALL_SEK or None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_consume_source())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Kuechendisplay Haus Beck", lifespan=lifespan)


class ConnectionManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._clients.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def broadcast(self, message: dict) -> None:
        async with self._lock:
            clients = list(self._clients)
        for ws in clients:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)


manager = ConnectionManager()


async def push_state() -> None:
    await manager.broadcast(service.snapshot())


async def _consume_source() -> None:
    """Speist Rohbons aus der aktiven BonSource in den Service und pusht danach."""
    async for roh_text in source.stream():
        try:
            service.ingest_bon(roh_text)
        except Exception as exc:  # nie blind: ein kaputter Bon stoppt nicht den Betrieb
            print(f"[ingest] Fehler beim Verarbeiten eines Bons: {exc}")
        await push_state()


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        await ws.send_json(service.snapshot())
        while True:
            msg = await ws.receive_json()
            _handle_action(msg)
            await push_state()
    except WebSocketDisconnect:
        await manager.disconnect(ws)
    except Exception:
        await manager.disconnect(ws)


def _handle_action(msg: dict) -> None:
    typ = msg.get("type")
    if typ == "item_fertig":
        service.item_fertig(int(msg["item_id"]))
    elif typ == "hauptgang_start":
        service.hauptgang_start(int(msg["ticket_id"]))
    elif typ == "zurueckholen":
        service.zurueckholen(int(msg["ticket_id"]))


# ---------- Dev-/Test-Endpunkte (ersetzen das Mockup-"＋ Bon") ----------
@app.post("/dev/bon")
async def dev_bon() -> JSONResponse:
    bon = await source.inject()
    return JSONResponse({"ok": True, "bon": bon})


@app.post("/dev/bon/custom")
async def dev_bon_custom(request: Request) -> JSONResponse:
    roh_text = (await request.body()).decode("utf-8")
    bon = await source.inject(roh_text)
    return JSONResponse({"ok": True, "bon": bon})


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "aktive_tickets": len(service.snapshot()["tickets"])}


# ---------- Statisches Frontend ----------
if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/", response_model=None)
async def index():
    index_html = FRONTEND_DIST / "index.html"
    if index_html.is_file():
        return FileResponse(index_html)
    return HTMLResponse(
        "<h1>Kuechendisplay</h1><p>Frontend noch nicht gebaut. "
        "Im Ordner <code>frontend/</code>: <code>npm install &amp;&amp; npm run build</code>.</p>",
        status_code=200,
    )
