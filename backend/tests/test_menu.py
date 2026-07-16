import menu


def test_gang_mapping_per_kategorie():
    # Vorspeise-Gruppe
    assert menu.resolve(27).dish.gang == "Vorspeise"   # Huehnersuppe (suppe)
    assert menu.resolve(26).dish.gang == "Vorspeise"   # Saganaki (vorspeise_warm)
    # Hauptgang
    assert menu.resolve(1).dish.gang == "Hauptgang"    # Gyros (grill)
    assert menu.resolve(89).dish.gang == "Hauptgang"   # Rumpsteak (steak)
    assert menu.resolve(126).dish.gang == "Hauptgang"  # Bauernsalat (salat)


def test_vorspeisen_kalt_und_dessert_und_beilagen():
    # Kollisionsfreie eindeutige Nummern aus den Zusatz-Sektionen pruefen wir
    # ueber Namens-Gegenprobe, weil nr sich mit `gerichte` ueberschneidet.
    assert menu.resolve(150).dish.gang == "Dessert"    # Coupe Danmark (nur dessert)
    assert menu.resolve(139).dish.gang == "Hauptgang"  # Pommes (beilage)


def test_kollision_nr5_wird_per_name_aufgeloest():
    r_haupt = menu.resolve(5, "Souvflaki")
    assert r_haupt.dish.name == "Souvflaki"
    assert r_haupt.ambiguous is True

    r_vor = menu.resolve(5, "Olivenmarmelade")
    assert r_vor.dish.name == "Olivenmarmelade"
    assert r_vor.ambiguous is True


def test_kollision_ohne_name_bevorzugt_hauptgericht():
    r = menu.resolve(5)
    assert r.ambiguous is True
    assert r.dish.sektion == "gerichte"


def test_unbekannte_nummer():
    r = menu.resolve(9999)
    assert r.unknown is True
    assert r.dish is None


def test_leere_nummer():
    r = menu.resolve(None)
    assert r.unknown is True
