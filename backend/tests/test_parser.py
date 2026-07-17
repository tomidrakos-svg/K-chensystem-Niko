from parser import parse_bon


# ---------- echtes Schultes-Format ----------
def test_echtes_format_tisch_positionen_notiz():
    bon = ("#0004\n17.07.2026        13:25\nTisch 41\n"
           "1  4 GYROS UEBERBACKEN        *13,90\n"
           "   TORA FERTIG MACHEN\n"
           "1  10 BIFTEKI              *13,90\nK 4\n")
    p = parse_bon(bon)
    assert p.tisch == "41"
    assert p.uhrzeit == "13:25"
    assert len(p.items) == 2
    assert p.items[0].menge == 1 and p.items[0].nr == 4
    assert p.items[0].name == "GYROS UEBERBACKEN"        # Preis entfernt
    assert p.items[0].notiz == "TORA FERTIG MACHEN"
    assert p.items[1].nr == 10 and p.items[1].name == "BIFTEKI"


def test_garstufe_als_eigene_zeile():
    bon = "Tisch 52\n1  81 STEAK MENUE       *24,90\n   MEDIUM\n"
    p = parse_bon(bon)
    assert p.items[0].garstufe == "medium"


def test_gang_marker_wird_uebersprungen():
    bon = ("Tisch 32\n*** VORSPEISE ***\n1  10 ZAZIKI       *5,90\n"
           "1  38 PLATTE POSEIDON        *21,50\n")
    p = parse_bon(bon)
    assert len(p.items) == 2                             # Marker ist kein Artikel
    assert p.items[0].nr == 10 and p.items[0].name == "ZAZIKI"
    assert p.items[1].nr == 38


def test_beilage_ohne_nr():
    bon = "Tisch 34\n1  128 THUNFISCHSALAT   *15,50\n1  REIS\n"
    p = parse_bon(bon)
    assert p.items[1].nr is None and p.items[1].name == "REIS"


def test_menge_groesser_eins():
    p = parse_bon("Tisch 34\n4  10 BIFTEKI   *55,60\n")
    assert p.items[0].menge == 4 and p.items[0].nr == 10


def test_freitext_nach_artikel_wird_notiz():
    p = parse_bon("Tisch 1\n1  1 GYROS\nrote bete\nund weiter\n")
    assert len(p.items) == 1
    assert "rote bete" in p.items[0].notiz and "und weiter" in p.items[0].notiz


def test_freitext_ohne_vorherigen_artikel_bleibt_rohzeile():
    p = parse_bon("Tisch 1\nHERRENLOSE ZEILE\n")
    assert len(p.items) == 1 and p.items[0].unparsbar is True


def test_fehlender_header_bleibt_betriebsfaehig():
    p = parse_bon("1  1 GYROS\n")
    assert p.tisch == "?" and len(p.items) == 1


# ---------- altes Simulator-Format bleibt lesbar (keine Regression) ----------
def test_altes_format_mit_x_und_pfeilnotiz():
    bon = "TISCH 12    18:42\n2x  1  Gyros\n1x  27  Huehnersuppe\n    >> medium\n"
    p = parse_bon(bon)
    assert p.tisch == "12" and p.uhrzeit == "18:42"
    assert p.items[0].menge == 2 and p.items[0].nr == 1 and p.items[0].name == "Gyros"
    assert p.items[1].garstufe == "medium"


def test_separatoren_werden_ignoriert():
    bon = "TISCH 1  12:00\n------------------------\n1x  1  Gyros\n========\n"
    p = parse_bon(bon)
    assert len(p.items) == 1
