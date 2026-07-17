# Setup vor Ort — Befunde (aus Fotos, 17.07.2026)

Aus den Setup-Fotos und echten Küchenbons abgeleitet. Grundlage für die reale
Anbindung.

## Hardware
- **Kasse:** **Schultes S-700 flextouch+** (Schultes Microcomputer-Vertriebs GmbH,
  Kassensysteme, made in Germany). Anschlüsse: 10/100BaseT **LAN** (belegt), USB,
  COM 1, COM 2, Peripherie, 2× Schublade.
- **Drucker:** **Bixolon** Thermodrucker (mehrere, gestapelt).
- **Küchen-Stationen** in der Kasse als „K2 / K3 / K4" adressiert; unsere Bons
  tragen den Fuß **„K 4"**.

## Entscheidend: der Küchendrucker hängt SERIELL
Der „Drucker Status"-Screen der Kasse listet:
- **Küchendrucker → COM2 (seriell / RS-232)**  ← hier läuft unser Bon-Strom
- Kassendrucker 2 → USB

### Empfohlener Anschlussweg: passiver Serial-Tap
Weil der Küchendrucker **seriell an COM2** hängt, ist der sauberste Weg ein
**passiver Serial-Tap**: ein USB-Seriell-Adapter am Pi liest die Datenleitung
(TX Kasse → Drucker) über einen Y-Abgriff **nur mit** (read-only).
- **Wirklich passiv** → fällt der Pi aus, druckt die Küche unverändert weiter
  (erfüllt Handoff §1/§2). Kein TCP-9100-Impersonieren, kein Epson-APG-Handshake.
- **Kein Eingriff** in die Kassenkonfiguration nötig.
- Ersetzt die frühere 9100-Netzwerk-Überlegung (siehe `scripts/kiosk/README.md`),
  weil der Drucker gar nicht am Netz hängt.

**Noch zu klären:** serielle Parameter von COM2 (Baudrate/Parität, z. B. 9600 8N1)
— aus den Schultes-Drucker-Einstellungen oder dem Bixolon-Selbsttest. Und das
genaue **Bixolon-Modell** (Stecker/Pinout).

## Bon-Format (geeicht, siehe `backend/parser.py`)
```
#0004
17.07.2026        13:25          ← Datum + Uhrzeit (Eingang)
Tisch 41
*** VORSPEISE ***                ← Gang-Marker (auch HAUPTSPEISE); erkannt/übersprungen
1  4 GYROS ÜBERBACKEN     *13,90  ← <menge>  <nr> <NAME>   *<preis>
   TORA FERTIG MACHEN            ← Notiz (eigene Zeile)
1  10 BIFTEKI            *13,90
   MEDIUM                        ← Garstufe (eigene Zeile)
1  REIS                          ← Beilage/Extra, teils ohne Nr
K 4                              ← Küchen-Station
```

## `menu.json`-Abgleich (aus den echten Bons)
- ✅ **Passt:** 1, 7, 10, 12, 15, 18, 19, 20, 38, 57, 111, 112, 128, 138
- ✅ **Kollision real bestätigt:** `10` = **Zaziki** (Vorspeise) *und* **Bifteki**
  (Hauptgang) — der Parser löst das über Name + case-insensitiven Abgleich.
- ⚠️ **Abweichung:** `4` druckt als **GYROS ÜBERBACKEN**, in `menu.json` ist 4 =
  „Gyros in Metaxasauce". → per Bon nicht sicher; **PLU-Liste klärt es**.
- ⚠️ **Fehlt in `menu.json`:** `81` = STEAK MENÜ, `146` = DICKE BOHNEN
  → werden als „unbekannt" angezeigt (nie blind), bis ergänzt.

## Offene Punkte für die reale Anbindung
1. **Artikel-/PLU-Liste** aus der Schultes-Kasse (Nr → Name) — löst Abweichungen &
   Kollisionen endgültig.
2. **COM2-Serial-Parameter** (Baud/Parität).
3. **Bixolon-Modell** (Rückseiten-Foto/Label) für den Tap-Stecker.
4. Ob die Schultes-Kasse eine **offene Schnittstelle/API** hat (beim Anbieter
   erfragen) — der Serial-Tap braucht sie nicht, wäre aber eine Alternative.
