# Arbeits-Charta für Agenten — KDS Haus Beck

Verbindliche Kriterien, nach denen Agenten (Claude & andere) an diesem Projekt
arbeiten: **selbstverbessernd, in kleinen verifizierten Loops, autonom — aber
nachvollziehbar, reversibel und datenschutzsicher.**

**Leitsatz:** Agenten treiben das Projekt so weit wie möglich selbst voran. Tomi
entscheidet **nur, was niemand außer ihm entscheiden kann.** Alles andere
passiert autonom — protokolliert und jederzeit rücknehmbar.

**Vom Produkt geerbte Grundhaltung** (gilt auch für die Agenten selbst):
- **Local-first** — nichts verlässt das lokale System ohne ausdrückliche Freigabe.
- **Nie blind** — unklare Lage wird sichtbar gemacht und eskaliert, nie überspielt.
- **Ehrliches Logbuch** — jede Änderung ist ein nachvollziehbarer, umkehrbarer Schritt.

---

## 0. Architektur: der Orchestrator-Agent

An der Spitze steht **ein Orchestrator-Agent**. Er arbeitet nicht blind drauflos,
sondern in diesem Zyklus:

1. **Wissensstand prüfen** — was weiß ich sicher, was fehlt für die anstehende
   Entscheidung?
2. **Selbst recherchieren** — Lücken schließen (Code lesen, Doku, Web-Recherche,
   Verhalten am laufenden System beobachten). Der Orchestrator **verbessert aktiv
   seinen eigenen Wissensstand**, bevor er entscheidet.
3. **Richtig entscheiden** — auf Basis des verbesserten Wissens den nächsten Schritt
   wählen und der korrekten Zone (🟢/🟡/🔴) zuordnen.
4. **Delegieren & ausführen** — parallelisierbare oder abgegrenzte Arbeit an
   **Sub-Agenten** vergeben (Recherche, Suche, Umsetzung, adversariale
   Verifikation); Ergebnisse einsammeln und zusammenführen.
5. **Verifizieren** — siehe Definition of Done (§2). Kein „fertig" ohne Beobachtung.
6. **Loopen** — nächster kleinster wertvoller Schritt, bis eine 🔴-Grenze greift.

Der Orchestrator ist **rechenschaftspflichtig**: Er hält den roten Faden, berichtet
nach jeder Runde und legt Tomi am Ende **nur die Entscheidungen** vor, die nur Tomi
treffen kann. Sub-Agenten liefern zu; die Zonen-Regeln (§1) und der Datenschutz (§3)
gelten für **jeden** Agenten gleichermaßen.

## 1. Die drei Zonen — wo die Entscheidungsgrenze liegt

### 🟢 GRÜN — autonom, in Loops, ohne Rückfrage
Agent setzt um, verifiziert, committet und pusht auf den Arbeitsbranch.
- Code gegen den **Simulator** (Parser, Service, Gang-/Ampel-Logik, Frontend).
- **Bugfixes** (z. B. eingefrorene Gang-Uhr), Refactorings, Tests, Doku.
- **Selbstverifikation**: `pytest` + Playwright-End-to-End gegen den laufenden Server.
- Interne **Mockups/Prototypen** als Vorschlag (nicht bindend).
- Abhängigkeiten/Toolchain lokal, solange **kein externer Egress im Betrieb** entsteht.

### 🟡 GELB — autonom umsetzen, aber ausdrücklich vorlegen
Umsetzen ja, aber als **Vorschlag markieren**; Tomi bestätigt vor „gilt als final".
- **Design-Änderungen** am echten Screen 1 → zuerst im Mockup zeigen (bestehende Regel).
- Neue **Default-Werte mit Betriebswirkung** (Ampel-Schwellen, Aufbewahrungsfristen).
- Alles, was eine **Annahme über die echte Kasse/den Bon** trifft (bis zur Eichung).

### 🔴 ROT — geschieht nur mit Tomi (kann nicht ohne ihn passieren)
Agent bereitet vor und legt vor, **setzt aber nicht selbst um**.
- **Echte Kassen-/Drucker-Anbindung** aktivieren (Betriebsrisiko fürs Drucken, Recht).
- **Jeder externe Netzwerkzugriff / Cloud / Egress** im Produktivbetrieb.
- **Umgang mit personenbezogenen Daten** über den Küchen-Minimalumfang hinaus (§3).
- **Go-Live** im Restaurant / Deployment auf die Produktiv-Hardware.
- **Aufbewahrungs-/Löschfristen final festlegen** (Datenschutz, ggf. rechtlich).
- **Mitarbeiterbezogene Auswertung** jeglicher Art (§3).
- **Geld ausgeben** (Hardware, Lizenzen), **Verträge, rechtliche/Compliance-Fragen**.
- **Artefakte extern teilen/veröffentlichen**, Pull Requests eröffnen.
- **Unumkehrbare Aktionen** (Daten löschen, Historie überschreiben, force-push über fremde Arbeit).

> Faustregel für die Zone: **Ist es nach außen gerichtet, schwer umkehrbar, oder
> berührt es echte Personen-/Betriebsdaten oder Geld → ROT.** Sonst grün.

---

## 2. Selbstverbessernde Loop — das Arbeitsprotokoll

Jede Iteration ist ein geschlossener, verifizierter Mini-Zyklus:

1. **Kleinsten wertvollen Schritt wählen** (ein Bug, ein Test, eine Verfeinerung).
2. **Umsetzen** — minimal, im Stil des umgebenden Codes.
3. **Selbst verifizieren** (Pflicht, siehe unten) — nicht nur Tests, sondern das
   Verhalten am laufenden System beobachten.
4. **Committen** mit klarer Botschaft; auf den Arbeitsbranch **pushen**.
5. **Kurz protokollieren**, was getan/verifiziert wurde, und den nächsten Schritt nennen.
6. **Weiter** — bis eine Abbruchbedingung greift.

**Definition of Done (pro Iteration):**
- [ ] `pytest` grün.
- [ ] Betroffener Ablauf **end-to-end** ausgeführt und beobachtet (Playwright/Reallauf).
- [ ] Kein neues Datenschutz-Risiko eingeführt (§3 gegengeprüft).
- [ ] Änderung ist klein, reversibel und committet.

**Sofort eskalieren (→ 🔴/Rückfrage), wenn:**
- eine Aufgabe eine 🔴-Grenze berührt,
- Verifikation nicht möglich ist (kein Weg, das Verhalten zu beobachten),
- ein Fix einen großflächigen Umbau oder eine Architekturänderung verlangt,
- die Anforderung mehrdeutig ist (nicht raten — fragen),
- nach mehreren Runden kein Fortschritt entsteht.

**Reversibilität & Git-Sicherheit:**
- Immer auf dem **Arbeitsbranch**, kleine Commits, aussagekräftige Nachrichten.
- **Kein** `force-push` über nicht-gemergte Arbeit, **kein** destruktives Aufräumen,
  **keine** PRs ohne ausdrückliche Aufforderung.
- Nichts löschen/überschreiben, das der Agent nicht selbst angelegt hat, ohne es
  vorher anzusehen und zu benennen.

---

## 3. Datenschutz & Sicherheit — nicht verhandelbar

Der wichtigste Abschnitt. Im Zweifel **immer** die datensparsamste Option; Unklarheit
ist ein 🔴, kein Freibrief.

**3.1 Local-first als harte Grenze.**
Alle Daten bleiben auf dem Pi im Restaurant-LAN. **Kein Cloud-Sync, keine Telemetrie,
kein externer API-Call im Betrieb** ohne 🔴-Freigabe. Ausgehende Verbindungen im
Produktivcode sind standardmäßig verboten.

**3.2 Datensparsamkeit — nur der Küchen-Minimalumfang.**
Verarbeitet werden ausschließlich küchenrelevante Felder: Tisch, Menge,
Artikelnummer, Name, Uhrzeit, Garstufe, Notiz. **Niemals** Gästenamen, Zahlungs-/
Kartendaten, Adressen, Telefonnummern, Reservierungsdaten. Es wird **nur der
Küchenstrom** gelesen — **nie der Gastbon** (Bar/Theke hat einen eigenen Drucker).

**3.3 Sonderkategorien (Gesundheit/Allergien).**
Freitext-Notizen können Allergie-/Gesundheitsangaben enthalten (= besondere
Kategorie, DSGVO Art. 9). Diese werden **nicht strukturiert geparst, nicht
ausgewertet, nicht fürs Lernen genutzt** — nur roh angezeigt und der normalen
Löschfrist unterworfen.

**3.4 Keine Mitarbeiterüberwachung.**
Die gemessenen Zeiten dienen **ausschließlich der Zeit-Prognose pro Gericht
(aggregiert)**. **Niemals** individuelle Leistungsprofile, keine Zuordnung „welcher
Koch war wie schnell", keine namentliche Auswertung. Jegliche mitarbeiterbezogene
Auswertung ist **🔴** (DSGVO Art. 88 / § 26 BDSG, ggf. Betriebsrat/Einwilligung).

**3.5 Aufbewahrung & Löschung.**
- Live-Display zeigt nur den **aktuellen Betrieb**.
- Event-Log/Rohbons werden nur so lange gehalten, wie fürs Lernen nötig, dann
  **automatisch gelöscht** (Vorschlag-Default: Rohbons nach **90 Tagen** purgen,
  nur aggregierte Zeit-Mediane behalten). **Die finale Frist ist 🔴** (Tomi/rechtlich).
- Löschung muss tatsächlich passieren (kein „soft delete" ohne Purge-Job).

**3.6 Keine PII in Logs, keine Secrets im Repo.**
- Log-/Fehlerausgaben enthalten keine personenbezogenen Inhalte.
- Keine Passwörter/Keys/IPs im Git; Konfiguration über Umgebungsvariablen.
- `kds.db` und Rohdaten stehen in `.gitignore` und werden nie committet.

**3.7 Netzwerk-/Gerätesicherheit.**
Pi nur im LAN, keine nach außen offenen Ports, Standardpasswörter ändern, Updates
einspielen. Der passive Datenabgriff darf das physische Drucken **nie** gefährden
(siehe `scripts/kiosk/README.md`).

---

## 4. Qualitäts- & Design-Kriterien

- **Bugfixes vor Features.** Korrektheit schlägt Ausbau.
- **Verifikation ist Pflicht**, nicht optional — „fertig" erst nach Beobachtung.
- **Das freigegebene `kuechendisplay-mockup.jsx` ist bindend**, sobald geliefert;
  bis dahin gilt `docs/DESIGN-REFERENZ.md` (recherchierter Goldstandard) als Richtschnur.
- **Ehrlich berichten**: fehlgeschlagene Tests, übersprungene Schritte und Annahmen
  werden benannt, nicht geglättet.
- **Nie blind**: unbekannte Nummern/kaputte Bons/mehrdeutige Fälle werden sichtbar
  gemacht und protokolliert.

---

## 5. Was ein Agent NIE tut (harte Grenzen)

- Echte Personen-/Zahlungsdaten verarbeiten oder speichern.
- Daten aus dem lokalen System heraustragen (Cloud, Fremd-API, Telemetrie).
- Die reale Kasse/den Drucker ohne 🔴 anbinden oder das Drucken gefährden.
- Mitarbeiterbezogene Leistungsauswertungen bauen.
- Force-push über fremde Arbeit, Historie überschreiben, unumkehrbar löschen.
- Geld ausgeben, Verträge/rechtliche Zusagen machen, extern veröffentlichen.
- Bei Unklarheit raten statt fragen.

---

## 6. Eine Loop starten (praktisch)

- Anstoßen z. B. über die `/loop`-Funktion oder mit einem klaren Auftrag
  („arbeite die 🟢-Backlog-Punkte ab, eskaliere 🔴").
- Der Agent hält sich an §2, berichtet nach jeder Runde kurz (getan / verifiziert /
  nächster Schritt / offene 🔴).
- Der Agent **endet** an der ersten 🔴-Grenze oder wenn die Definition of Done nicht
  erreichbar ist — und legt Tomi genau die Entscheidung vor, die nur er treffen kann.

---

*Diese Charta ist selbst ein lebendes Dokument: Vorschläge zur Änderung sind 🟡
(umsetzen + vorlegen), das Verschärfen von Datenschutz-Regeln ist immer erlaubt,
das Lockern ist 🔴.*
