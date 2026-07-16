# Kassen-Checkliste (Foto-Rundgang vor Ort)

Zum Abarbeiten im Restaurant. Mach die Fotos in dieser Reihenfolge und schick sie
als „Foto 1, Foto 2 …" — dann ordne ich sie direkt zu und leite das Bon-Format
sowie den Anschlussweg ab. **Wichtigstes ist Abschnitt B (echte Bons).**

## A · Kasse identifizieren
- [ ] **Foto 1** — Kasse von vorne (ganzes Gerät, Marke/Logo sichtbar).
- [ ] **Foto 2** — Typenschild/Aufkleber an Unterseite oder Rückseite (Modell + Seriennummer).
- [ ] **Foto 3** — „Info/Über"-Screen der Kassen-Software (Name + Version), falls zugänglich.
- [ ] **Foto 4** — Unterkante eines **Gast**bons (dort steht oft die Software/der Anbieter).

## B · Echte Bons — das Wichtigste fürs Parsen
> Tipp: Bon flach hinlegen, **gerade von oben**, scharf, **ganzer** Bon inkl. Kopf und Fuß.
- [ ] **Foto 5** — Küchenbon **mit Vorspeise + Hauptgang** (zeigt, wie Gänge getrennt werden).
- [ ] **Foto 6** — Küchenbon **mit Garstufe** (Steak/Medaillons — wie steht „medium/blutig/durch" drauf?).
- [ ] **Foto 7** — Küchenbon **mit Beilagenänderung/Notiz/Sonderwunsch**.
- [ ] **Foto 8** — Küchenbon einer **großen Bestellung** (mehrere Positionen, Menge > 1).

## C · Küchendrucker
- [ ] **Foto 9** — Drucker von vorne (Marke/Modell).
- [ ] **Foto 10** — Drucker von **hinten**: Anschlüsse sichtbar — **LAN/Ethernet-Buchse? USB? Seriell?** — samt eingesteckter Kabel.
- [ ] **Foto 11** — *Falls möglich:* Selbsttest-/Konfig-Ausdruck des Druckers (zeigt die **IP-Adresse**).
      Tipp: Viele Thermodrucker drucken das, wenn man beim **Einschalten die Papiervorschub-Taste gedrückt hält**.

## D · Netzwerk & Stromplatz
- [ ] **Foto 12** — Switch/Router am Druckerplatz (freie LAN-Ports?) und wie der Drucker angeschlossen ist.
- [ ] **Foto 13** — Steckdosen-/Platzsituation am Druckerplatz (für den Raspberry Pi).

## E · Kassen-Einstellungen (optional, braucht Admin-Zugang)
- [ ] **Foto 14** — Drucker-/Stationseinstellungen der Kasse (Screenshot): **Kann die Kasse auf ZWEI Ziele drucken?**
- [ ] **Foto 15** — Hersteller-Portal/Account-Name, falls vorhanden (für die API-Frage).

## Kurze Fragen (keine Fotos — einfach beantworten)
- [ ] Gibt es eine **offene API/Schnittstelle** zur Kasse? (Anbieter fragen) → falls ja, entfällt der Drucker-Abgriff.
- [ ] Erlaubt die Kasse einen **zweiten Küchendrucker / ein zweites Druckziel**?
- [ ] **Marke, Modell, Software-Version** der Kasse (kurz notiert).
- [ ] Ist der Küchendrucker **per LAN** angeschlossen oder **USB**?

---

### Das absolute Minimum, falls die Zeit knapp ist
**Foto 5–8** (echte Küchenbons) + **Foto 10** (Drucker-Rückseite) + die vier Fragen oben.
Damit kann ich Parser-Format und Anschlussweg festlegen.
