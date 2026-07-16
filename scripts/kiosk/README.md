# Kiosk-Einrichtung — Raspberry Pi + iPad

Ziel (Handoff §1/§2): Der Pi ist das ganze Hirn (greift Bons ab, speichert in
SQLite, serviert das Display). Das iPad ist nur ein Browser im Vollbild. iPad
einschalten = Küche. Kein Login, keine Einstellungen im Betriebs-Screen.

## 1. Backend auf dem Pi als Dienst

```bash
# einmalig
cd ~/K-chensystem-Niko/backend
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
# Frontend bauen (Node nötig)
cd ../frontend && npm install && npm run build

# Dienst installieren (Autostart beim Boot)
sudo cp ~/K-chensystem-Niko/scripts/kiosk/kds.service /etc/systemd/system/
sudo systemctl enable --now kds.service
```

Danach läuft das Display unter `http://<pi-ip>:8000/`. Prüfen: `curl http://<pi-ip>:8000/health`.

## 2. iPad im Kiosk-Modus (Geführter Zugriff)

1. Safari öffnen → `http://<pi-ip>:8000/`.
2. Zum Home-Bildschirm hinzufügen (Vollbild ohne Browser-Leiste).
3. **Einstellungen → Bedienungshilfen → Geführter Zugriff** aktivieren.
4. Display-App öffnen, Seitentaste 3× → Geführter Zugriff startet. Damit bleibt
   das iPad in der App, auch beim versehentlichen Wischen.
5. **Automatische Sperre = Nie** (Einstellungen → Anzeige & Helligkeit).
6. Halterung auf Augenhöhe, robuste Hülle (iPad ist Verschleißteil, Handoff §11).

## 3. Reale Bon-Anbindung (erst nach Bon-Foto-Eichung)

> **Wichtig (Recherche-Korrektur zum Handoff):** „Passives Mithören" auf TCP 9100
> ist in der Praxis **kein** passiver Wire-Tap. Wer auf 9100 lauscht, ist der
> Drucker-*Endpunkt* und muss Epson-APG-Statusabfragen (`DLE EOT`/`ENQ`/`DC4`)
> beantworten, sonst hält die Kasse den „Drucker" für offline und sendet nicht.
> Das kollidiert mit „fällt der Pi aus, druckt die Küche weiter". Deshalb gibt es
> drei tragfähige Anschluss-Optionen — die reale Quelle wird hinter
> `backend/bonsource.py::PrinterTcpSource` eingehängt, ohne dass sich Service/UI
> ändern.

| Option | Wie | Bewertung |
|---|---|---|
| **(a) Zwei-Ziel-Druck** | Kasse druckt den Küchenbon auf **zwei** Ziele: echter Drucker **und** Pi. | **Empfohlen.** Echter Drucker bleibt unberührt; fällt der Pi aus, druckt die Küche weiter. Setzt voraus, dass die Kasse zwei Küchendrucker/Ziele erlaubt. |
| **(b) SPAN/Mirror-Port** | Managed Switch spiegelt den Drucker-Port auf den Pi. | Echtes passives Mithören, Pi nie im Druckpfad. Braucht Managed Switch. |
| **(c) Inline-Proxy** | Kasse → Pi → Drucker (Pi reicht durch und kopiert mit). | Notlösung. Single Point of Failure: fällt der Pi aus, stoppt der Druck. Nur wenn (a)/(b) nicht möglich. |

Mit **Port 9100** (RAW/JetDirect) beginnen. LPD (515) nur, falls die konkrete
Kasse es nutzt.

## 4. Vor Ort zu klären (Handoff §10)

- Küchendrucker-Anschluss: LAN vs. USB (Foto der Rückseite).
- Ein echtes Küchenbon-Foto → Parser-Format in `backend/parser.py` eichen und den
  Simulator danach ausrichten.
- Kassen-Marke/-Modell (steht meist unten auf dem Gastbon) — bei offener API
  entfällt der Drucker-Abgriff ganz.
- Welche `nr` die Kasse bei Kollisionen (z. B. Nr. 3, 5) tatsächlich sendet.
