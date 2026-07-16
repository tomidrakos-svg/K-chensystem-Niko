"""Integrationstest der WebSocket-/HTTP-Schicht mit dem echten App-Objekt."""
import os
import tempfile

# Test-DB und Export-Ordner isolieren, BEVOR das App-Modul sie liest.
os.environ["KDS_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "kds_test.db")
os.environ["KDS_EXPORT_DIR"] = tempfile.mkdtemp()

from starlette.testclient import TestClient  # noqa: E402

import app as app_module  # noqa: E402


def test_health_und_custom_bon_und_ws():
    client = TestClient(app_module.app)
    with client:  # loest startup/shutdown aus
        with client.websocket_connect("/ws") as ws:
            initial = ws.receive_json()
            assert initial["type"] == "snapshot"

            # Bon ueber Custom-Endpunkt einspeisen ...
            r = client.post("/dev/bon/custom", content="TISCH 42  20:00\n2x  1  Gyros\n")
            assert r.json()["ok"] is True

            # ... und ihn als Live-Update ueber den WebSocket empfangen.
            update = ws.receive_json()
            assert update["type"] == "snapshot"
            assert any(t["tisch"] == "42" for t in update["tickets"])

    assert client.get("/health").json()["ok"] is True


def test_export_liste_und_download_und_traversal_schutz():
    d = app_module.EXPORT_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / "lernzeiten-2026-07-15.json").write_text('{"zeiten": []}', encoding="utf-8")
    client = TestClient(app_module.app)

    liste = client.get("/export")
    assert "lernzeiten-2026-07-15.json" in liste.text

    ok = client.get("/export/download/lernzeiten-2026-07-15.json")
    assert ok.status_code == 200 and ok.json() == {"zeiten": []}

    # Ungültiger Name / Path-Traversal -> 404 (kein Zugriff ausserhalb des Ordners).
    assert client.get("/export/download/geheim.json").status_code == 404
    assert client.get("/export/download/lernzeiten-2026-07-15.json.bak").status_code == 404
