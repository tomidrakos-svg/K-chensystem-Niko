"""Integrationstest der WebSocket-/HTTP-Schicht mit dem echten App-Objekt."""
import os
import tempfile

# Test-DB isolieren, BEVOR das App-Modul seine Verbindung aufbaut.
os.environ["KDS_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "kds_test.db")

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
