# Design-Goldstandard KDS — Referenz für Screen 1

Recherche des aktuellen Goldstandards etablierter Küchendisplays (Toast, Fresh
KDS / TouchBistro-KDS „powered by Fresh", Square, Branchen-UX) und Ableitung
konkreter Vorgaben für unseren Screen 1. Grundlage sind offizielle Vendor-Docs
und Feature-Seiten (Links unten).

> **Hinweis zu Screenshots:** Das Herunterladen/Anzeigen der Original-Screenshots
> ist in dieser Umgebung durch die Netzwerk-Policy gesperrt (der Gateway
> verweigert Fremd-Hosts wie `toasttab.com`, `fresh.technology`, `squareup.com`).
> Die Links unten öffnest du selbst, um die Screenshots zu sehen. Die Design-
> Angaben stammen aus den offiziellen Beschreibungen dieser Seiten.

---

## 1. Das Gesamtbild — worauf sich alle einig sind

Der Goldstandard ist erstaunlich einheitlich und deckt sich mit unserem Handoff:

- **Karten-Raster** („Tiled View" bei Fresh, „Grid" bei Toast): gleich große
  Kacheln, füllen den Schirm **oben→unten, links→rechts**, minimales Scrollen.
  Das ist genau unser Layout.
- **Dreistufige Farb-Eskalation** grün/neutral → gelb → rot, **zeitgesteuert**.
- **Coursing mit Hold & Fire**: Vorspeise zuerst, Hauptgang „hält" mit sichtbarem
  Hold-Indikator, wird per Tipp „gefeuert". Dessert hält bis Hauptgang. **Unser
  Modell 1:1.**
- **Bump & Recall**: Item/Ticket abhaken (bump), letzte Abgeschlossene zurückholen.
- **All-Day-View** (summierte offene Artikel) ist Standard-Bestandteil (bei uns
  Screen 2, später).
- **Große, kontrastreiche Sans-Serif**, aus Distanz lesbar; Dark-Mode üblich.

---

## 2. Farb- & Timer-Eskalation — konkrete Vendor-Defaults

Es gibt keine „offizielle" Norm, aber die beobachteten Defaults als Orientierung:

| System | gelb | orange | rot | Bemerkung |
|---|---|---|---|---|
| **Toast** | 8 min | 12 min | 15 min | konfigurierbar; alt. Beispiel 5/10/15 |
| **Square** | 5 min | — | 10 min | zweistufig, fix pro Screen |
| **Fresh KDS** | „caution" | — | „late" | **pro Bestelltyp** einstellbar (grün/gelb/rot) |

**Für uns:** Wir sind **prozentbasiert** (gelb ab 72 %, rot ab 100 % der
erwarteten Gang-Zeit) — das ist adaptiver als fixe Minuten und passt zu Fresh'
Philosophie „pro Kontext einstellbar". Empfehlung: **beibehalten**, aber die
Schwellen zusätzlich als absolute-Minuten-Option anbieten (manche Köche denken in
Minuten). Vendor-Defaults oben als Startorientierung dokumentiert.

---

## 3. Karten-Anatomie (Ticket Card) — Soll für Screen 1

Konsolidiert aus den Vendor-Layouts, gemappt auf unseren Stand:

| Element | Goldstandard | Unser Screen 1 | Verdikt |
|---|---|---|---|
| Kopf: Tischnummer | groß, dominant | Tischnr riesig | ✅ haben |
| Kopf: Zeit/Alter | Bonzeit + laufender Timer | Bonzeit + „vor X min" | ✅ haben |
| Gang-Trennung | Kurse mit eigener Zeile/Label | Gang-Gruppen mit Label | ✅ haben |
| Timer pro Kurs | Uhr + Fortschritt | Uhr + füllende Zeitleiste | ✅ haben |
| Hold-Indikator | „HOLD"-Badge am geparkten Kurs | nur gedimmt + Button | 🟡 **Badge ergänzen** |
| Modifier/Notiz | farblich hervorgehoben (bold/Farbe) | gelbe »-Zeile | ✅ haben |
| Garstufe | Badge am Gericht | Gold-Badge | ✅ haben |
| Fire-Aktion | „Fire course"-Tap | goldener „Hauptgang starten" | ✅ haben |
| Bump | Item/Karte abhaken | Tap = durchstreichen | ✅ haben |
| Recall | Ablage/Button | Zurückholen-Ablage unten | ✅ haben |

**Empfohlene Verfeinerungen (klein, hoher Effekt):**
1. **Hold-Badge** am geparkten Hauptgang/Dessert (z. B. „WARTET"/„HOLD"), nicht nur
   Dimmen — Goldstandard macht den Hold-Zustand explizit sichtbar.
2. **Item-Zähler/Progress** pro Kurs („2/3 fertig"), damit der Fortschritt auf
   Distanz erkennbar ist.
3. **Rot-Zustand kräftiger** (voller Kartenhintergrund-Tint statt nur Rand) — das
   „sofort ins Auge"-Prinzip der Late-Tickets.

---

## 4. Typografie & Lesbarkeit (Betriebs-UX)

Aus den Signage-/Readability-Quellen (auf Küchen-Distanz übertragen):

- **Sans-Serif, Gewicht medium+**, auf Distanz getestet.
- **Kontrast** ≥ 4,5:1 (Minimum), 7:1 bevorzugt.
- **Dark-Mode** (heller Text auf dunkel) ist zum **Scannen** überlegen und
  spart bei Maximalhelligkeit Strom — passt zur Küche. Fresh bietet Light/Dark/
  System pro View.
- **Große Schrift**: Faustregel „1 inch Höhe pro 3 m Distanz". Für unser iPad auf
  Augenhöhe heißt das: Tischnummer sehr groß (haben wir), Gerichtnamen nicht unter
  ~17–18 px, eher größer.

**Für uns:** Dark-Theme ✅. Empfehlung: **Light-Mode-Variante** als Option
vorsehen (manche Küchen sind sehr hell) — genau das macht Fresh. Schriftgrößen der
Gerichte einen Tick größer testen.

---

## 5. Coursing / Hold & Fire — validiert

Wörtlich aus dem Goldstandard (TouchBistro/Fresh): *„appetizers fire first, mains
hold until appetizers bump, desserts hold until mains bump; the KDS knows the
order, displays a hold indicator on the main, and releases it the moment the
appetizer ticket clears."*

→ Deckt sich exakt mit unserer Gang-Logik. Einziger Unterschied: manche Systeme
**auto-feuern** den Hauptgang, sobald die Vorspeise gebumpt ist. Wir starten
**manuell per Tap** (Handoff-Vorgabe, bewusst). Optionale spätere Ausbaustufe:
„Auto-Fire nach Vorspeise-Bump" als umschaltbare Betriebsart.

---

## 6. Layout-Views (Fresh als Referenz)

Fresh bietet vier Modi — nützlich als Roadmap:
- **Tiled** = unser Raster (Standard). ✅
- **Classic** = eine horizontale Reihe (kleine Küchen).
- **Split** = zwei Reihen nach Bestelltyp (z. B. Dine-in / Takeout).
- **Take-Out** = Off-Premise mit Abholzeit.

**Für uns:** Tiled ist richtig für V1. Split/Take-Out erst relevant, falls Liefer-/
Abholgeschäft dazukommt — nicht jetzt.

---

## 7. Konkrete To-dos aus dieser Recherche

Klein, ohne Architektur-Änderung, schärfen Screen 1 Richtung Goldstandard:

- [ ] **HOLD/WARTET-Badge** am geparkten Kurs (statt nur Dimmen)
- [ ] **Kurs-Fortschritt** „x/y fertig" im Gang-Kopf
- [ ] **Rot-Zustand** als flächigeren Karten-Tint (nicht nur Rand)
- [ ] **Light-Mode-Variante** als Option (Küchenhelligkeit)
- [ ] Gerichtnamen-Schriftgröße auf Distanz gegenchecken
- [ ] Ampel-Schwellen zusätzlich als **absolute Minuten** konfigurierbar machen

> Diese Punkte sind **Verfeinerungen** und ersetzen NICHT das echte
> `kuechendisplay-mockup.jsx` — sobald das vorliegt, gilt es als verbindlich und
> wird darübergelegt.

---

## Quellen (Screenshots dort direkt ansehbar)

- Toast KDS – Produkt/Doku: <https://pos.toasttab.com/hardware/kitchen-display-system> · <https://doc.toasttab.com/doc/platformguide/platformKDSOverview.html> · <https://doc.toasttab.com/doc/platformguide/platformKDSWorkflowUsingCoursePacing.html>
- Fresh KDS – Features & Views: <https://www.fresh.technology/kitchen-display-system> · <https://www.fresh.technology/kds-features/tiled-view> · <https://www.fresh.technology/kds-features/classic-view> · <https://www.fresh.technology/kds-features/split-view> · <https://www.fresh.technology/kds-features/hold-fire-courses>
- Square KDS: <https://squareup.com/us/en/point-of-sale/restaurants/kitchen-display-system> · Play-Store (Screenshots): <https://play.google.com/store/apps/details?id=com.squareup.rst.kds>
- TouchBistro KDS (powered by Fresh): <https://www.touchbistro.com/help/articles/using-the-kds/> · <https://help.touchbistro.com/s/article/Using-TouchBistro-KDS-Powered-by-Fresh>
- UX-Fallstudie KDS (Designer-Perspektive): <https://gwenndesign.medium.com/product-design-case-study-kitchen-display-system-52a5e9cab81e>
- Lesbarkeit/Typografie (Signage, übertragbar): <https://seenlabs.com/blog/digital-menu-legibility-typography-contrast-standards-for-qsr-signage>
