# Liefer-Checkliste — was du besorgst, damit nichts vergessen wird

Diese Liste sammelt alles, was du (Tomi) liefern/klären musst, um das
Küchendisplay von **V1 (Simulator)** in den **echten Betrieb** zu bringen.
V1 läuft bereits ohne diese Punkte — sie schalten nur die reale Anbindung und
das Feintuning frei.

**Priorität:** 🔴 blockiert die reale Anbindung · 🟡 wichtig fürs Feintuning · ⚪ später (Screen 2/3, Lernen)

---

## 1. 🔴 Kasse & Bon — schaltet den echten Datenabgriff frei

Ohne das läuft das Display nur gegen den Simulator.

- [ ] **Foto eines echten Küchenbons** (scharf, gerade). Am besten mehrere Fälle:
  - [ ] Bon **mit Vorspeise + Hauptgang** (zeigt, wie Gänge getrennt werden)
  - [ ] Bon **mit Garstufe** (Steak/Medaillons — wie steht „medium" drauf?)
  - [ ] Bon **mit Beilagenänderung/Notiz** (wie wird der Sonderwunsch gedruckt?)
  - [ ] **Große Bestellung** (mehrere Tische/Positionen, Mengen > 1)
- [ ] **Kassen-Marke & -Modell** (steht meist unten auf dem **Gast**bon; sonst Foto der Kasse)
- [ ] **Hat die Kasse eine offene API / Schnittstelle?** (Hersteller fragen)
      → Falls ja, entfällt der Drucker-Abgriff ganz.
- [ ] **Drucker-Anschluss: LAN oder USB?** → **Foto der Drucker-Rückseite**
- [ ] **Kann die Kasse den Küchenbon auf ZWEI Ziele drucken?** (echter Drucker + Pi)
      → Das ist die empfohlene, ausfallsichere Anschluss-Option (a).
- [ ] **Managed Switch am Druckerplatz vorhanden?** (nur nötig für Option b / SPAN-Port)
- [ ] **Welche `nr` sendet die Kasse wirklich?** — besonders bei den Doppel-Nummern
      (siehe Punkt 3). Am echten Bon prüfen.

> Hintergrund/Details zu den Anschluss-Optionen: [`../scripts/kiosk/README.md`](../scripts/kiosk/README.md)

---

## 2. 🔴 Design-Referenz — das freigegebene Mockup fehlt

- [ ] **`kuechendisplay-mockup.jsx`** liefern.
      Der Handoff nennt es als abgenommene Design-Referenz (Farben, Typografie,
      Karten-Aufbau), aber es kam **nicht** mit. Screen 1 ist aktuell nach der
      Text-Beschreibung (§7) gebaut und wird danach exakt angeglichen.
- [ ] Gewünschte **Farben / Logo / Branding** (falls über das Mockup hinaus etwas soll)
- [ ] **Hell- oder Dunkel-Design?** (aktuell dunkel/kontraststark; Küche ist hell)

---

## 3. 🟡 Menü-Daten — Klärungen mit dem Koch/Wirt

- [ ] **Doppelte Nr. 3** (in `menu.json`: „Gyros und Leber" *und* „Trilogie 3 Dips"):
      welche Nummer sendet die Kasse tatsächlich für welches Gericht?
- [ ] **Weitere Nr.-Kollisionen** gegenchecken (z. B. 5, 6, 7 tauchen in mehreren
      Sektionen auf) — welche gehört zu welchem Artikel?
- [ ] **Zubereitungszeiten `prep_seed_min`** vom Koch plausibilisieren
      (aktuell Startwerte; steuern die Ampel, bis das System echte Zeiten lernt).
- [ ] **Garstufen-Wording der Kasse**: exakte Begriffe (blutig / englisch / medium /
      rosa / durch …) — der Parser erkennt sie namentlich.
- [ ] **Fehlen Gerichte?** Tageskarte, Aktionen, Saisonales, Getränke die in die
      Küche gehen?
- [ ] **Warme Vorspeisen** (Saganaki, Calamaris, Muscheln): laufen sie über
      Grill/Pfanne oder die Vorspeisen-/Salate-Seite? (erst für die spätere
      2. Station relevant)

---

## 4. 🟡 Netzwerk & Hardware vor Ort

- [ ] **LAN-Anschluss am Druckerplatz** frei / Switch-Port verfügbar?
- [ ] **Strom** am Druckerplatz für den Pi vorhanden?
- [ ] **Raspberry Pi + Gehäuse** beschafft?
- [ ] **iPad**: Modell vorhanden / zu beschaffen? Größe?
- [ ] **Robuste iPad-Hülle** (Verschleißteil in heißer, fettiger Küche, §11)
- [ ] **iPad-Halterung** auf Augenhöhe — Montageort geklärt?
- [ ] **WLAN im Restaurant**: SSID + Passwort (iPad muss den Pi erreichen)
- [ ] **Feste IP / Hostname für den Pi** im LAN (damit die Display-URL stabil bleibt)

---

## 5. 🟡 Betrieb & Ablauf — fürs Feintuning

- [ ] **Wer tippt „Hauptgang starten"?** Ablauf in der Küche kurz beschreiben.
- [ ] **Ziel-Zeiten pro Gang** (wann soll es gelb/rot werden?) — damit stellen wir
      die Ampel-Schwellen richtig ein (aktuell 72 % / 100 % der erwarteten Zeit).
- [ ] **Stoßzeiten** (Wochentage/Uhrzeiten) — wann testen wir sinnvoll?
- [ ] **Testbetrieb parallel zum Papier**: Termin, an dem das Display neben dem
      bestehenden Bon-Ablauf mitläuft, ohne ihn zu ersetzen.

---

## 6. ⚪ Später — Erweiterungen (nicht für den ersten Live-Betrieb)

- [ ] **Screen 2 „Tag" + All-Day-View** (summierte offene Gerichte, „4× Gyros offen")
- [ ] **Selbstlernen**: nach 2–4 Wochen echten Daten `prep_seed_min` durch gemessene
      Median-Zeiten ersetzen
- [ ] **Screen 3 „Lernen"** (gelernte Zeiten, Stoßzeiten-Muster)
- [ ] **Zweite Station** (Grill/Pfanne vs. Vorspeise/Salate) — eigenes iPad
- [ ] Entscheidung: Warme Vorspeisen-Zuordnung (siehe Punkt 3) für den Stations-Split

---

### Das absolute Minimum, um live zu gehen
Wenn du nur **drei Dinge** zuerst besorgst:
1. 📸 **Foto eines echten Küchenbons** (Punkt 1)
2. 🏷️ **Kassen-Marke/-Modell + API ja/nein** (Punkt 1)
3. 🎨 **das Mockup `kuechendisplay-mockup.jsx`** (Punkt 2)

Damit können wir Parser eichen, die Anbindung wählen und das Design final machen.
