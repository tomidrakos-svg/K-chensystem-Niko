from parser import parse_bon


def test_header_und_items():
    bon = "TISCH 12    18:42\n2x  1  Gyros\n1x  27  Huehnersuppe\n"
    p = parse_bon(bon)
    assert p.tisch == "12"
    assert p.uhrzeit == "18:42"
    assert len(p.items) == 2
    assert p.items[0].menge == 2 and p.items[0].nr == 1 and p.items[0].name == "Gyros"


def test_garstufe_und_notiz():
    bon = "TISCH 3  19:00\n1x  76  3 Rindermedaillons\n    >> medium\n1x  1  Gyros\n    >> ohne Zwiebeln\n"
    p = parse_bon(bon)
    assert p.items[0].garstufe == "medium"
    assert p.items[0].notiz is None
    assert p.items[1].garstufe is None
    assert p.items[1].notiz == "ohne Zwiebeln"


def test_mehrere_notizen_werden_gesammelt():
    bon = "TISCH 3  19:00\n1x  1  Gyros\n    >> ohne Zwiebeln\n    >> extra scharf\n"
    p = parse_bon(bon)
    assert "ohne Zwiebeln" in p.items[0].notiz
    assert "extra scharf" in p.items[0].notiz


def test_separator_zeilen_werden_ignoriert():
    bon = "TISCH 1  12:00\n------------------------\n1x  1  Gyros\n========\n"
    p = parse_bon(bon)
    assert len(p.items) == 1


def test_unparsbare_zeile_bleibt_als_rohzeile():
    bon = "TISCH 1  12:00\n1x  1  Gyros\nKRITZEL kaputte zeile ###\n"
    p = parse_bon(bon)
    assert len(p.items) == 2
    assert p.items[1].unparsbar is True
    assert "KRITZEL" in p.items[1].raw_line


def test_note_ohne_vorherigen_artikel():
    bon = "TISCH 1  12:00\n    >> herrenlos\n"
    p = parse_bon(bon)
    assert len(p.items) == 1
    assert p.items[0].unparsbar is True


def test_fehlender_header_bleibt_betriebsfaehig():
    bon = "1x  1  Gyros\n"
    p = parse_bon(bon)
    assert p.tisch == "?"
    assert len(p.items) == 1
