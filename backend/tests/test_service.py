import pytest

import config
import db
from service import KDSService


@pytest.fixture
def svc():
    return KDSService(db.connect(":memory:"))


def _gaenge(snap, ticket_id):
    t = next(t for t in snap["tickets"] if t["id"] == ticket_id)
    return {g["gang"]: g for g in t["gaenge"]}


def test_vorspeise_startet_sofort_hauptgang_geparkt(svc):
    tid = svc.ingest_bon("TISCH 5  19:00\n1x  27  Huehnersuppe\n2x  1  Gyros\n")
    g = _gaenge(svc.snapshot(), tid)
    assert g["Vorspeise"]["status"] == "laufend"
    assert g["Vorspeise"]["gestartet_at"] is not None
    assert g["Hauptgang"]["status"] == "geparkt"
    assert g["Hauptgang"]["gestartet_at"] is None


def test_ohne_vorspeise_startet_hauptgang_sofort(svc):
    tid = svc.ingest_bon("TISCH 6  19:00\n2x  1  Gyros\n")
    g = _gaenge(svc.snapshot(), tid)
    assert g["Hauptgang"]["status"] == "laufend"


def test_erwartete_zeit_ist_max_prep_seed(svc):
    # Gyros 8, Rindermedaillons 18 -> Gruppe erwartet 18
    tid = svc.ingest_bon("TISCH 6  19:00\n1x  1  Gyros\n1x  76  3 Rindermedaillons\n")
    g = _gaenge(svc.snapshot(), tid)
    assert g["Hauptgang"]["erwartet_min"] == 18


def test_hauptgang_start_startet_hauptgang(svc):
    tid = svc.ingest_bon("TISCH 5  19:00\n1x  27  Huehnersuppe\n2x  1  Gyros\n")
    svc.hauptgang_start(tid)
    g = _gaenge(svc.snapshot(), tid)
    assert g["Hauptgang"]["status"] == "laufend"


def test_alle_fertig_wandert_in_recall(svc):
    tid = svc.ingest_bon("TISCH 6  19:00\n2x  1  Gyros\n")
    snap = svc.snapshot()
    for it in snap["tickets"][0]["gaenge"][0]["items"]:
        svc.item_fertig(it["id"])
    snap = svc.snapshot()
    assert snap["tickets"] == []
    assert len(snap["recall"]) == 1
    assert snap["recall"][0]["id"] == tid


def test_zurueckholen_reaktiviert(svc):
    tid = svc.ingest_bon("TISCH 6  19:00\n1x  1  Gyros\n")
    it = svc.snapshot()["tickets"][0]["gaenge"][0]["items"][0]
    svc.item_fertig(it["id"])
    assert svc.snapshot()["recall"]
    svc.zurueckholen(tid)
    assert svc.snapshot()["tickets"]
    assert svc.snapshot()["recall"] == []


def test_geparktes_item_kann_nicht_fertig_werden(svc):
    tid = svc.ingest_bon("TISCH 5  19:00\n1x  27  Huehnersuppe\n1x  1  Gyros\n")
    g = _gaenge(svc.snapshot(), tid)
    gyros = g["Hauptgang"]["items"][0]
    svc.item_fertig(gyros["id"])  # Hauptgang geparkt -> ignorieren
    g = _gaenge(svc.snapshot(), tid)
    assert g["Hauptgang"]["items"][0]["fertig"] is False


def test_unbekannte_nr_bleibt_sichtbar(svc):
    tid = svc.ingest_bon("TISCH 9  19:00\n1x  9999  Raetselhaftes Gericht\n")
    g = _gaenge(svc.snapshot(), tid)
    item = g["Hauptgang"]["items"][0]
    assert item["unbekannt"] is True
    assert item["name"] == "Raetselhaftes Gericht"


def test_fertiger_gang_hat_abschlusszeit_zum_einfrieren(svc):
    # Ticket mit Vorspeise (startet sofort) + Hauptgang; nur Vorspeise abhaken.
    tid = svc.ingest_bon("TISCH 5  19:00\n1x  27  Huehnersuppe\n2x  1  Gyros\n")
    g = _gaenge(svc.snapshot(), tid)
    vor_item = g["Vorspeise"]["items"][0]
    assert g["Vorspeise"]["fertig_at"] is None      # noch laufend
    svc.item_fertig(vor_item["id"])
    g = _gaenge(svc.snapshot(), tid)
    assert g["Vorspeise"]["status"] == "fertig"
    # Abschlusszeit gesetzt -> das Frontend friert die Uhr darauf ein statt "jetzt".
    assert g["Vorspeise"]["fertig_at"] is not None
    # Laufender Hauptgang hat KEINE Abschlusszeit.
    assert g["Hauptgang"]["fertig_at"] is None


def test_dessert_ohne_hauptgang_ist_startbar(svc):
    # Vorspeise + Dessert, KEIN Hauptgang: Dessert parkt und muss startbar bleiben.
    tid = svc.ingest_bon("TISCH 30  19:00\n1x  27  Huehnersuppe\n1x  150  Coupe Danmark\n")
    g = _gaenge(svc.snapshot(), tid)
    assert g["Vorspeise"]["status"] == "laufend"
    assert g["Dessert"]["status"] == "geparkt"
    svc.hauptgang_start(tid)          # dieselbe Start-Aktion startet das Dessert
    g = _gaenge(svc.snapshot(), tid)
    assert g["Dessert"]["status"] == "laufend"


def test_snapshot_enthaelt_ampel_config(svc):
    snap = svc.snapshot()
    assert snap["config"]["gelb_pct"] == config.AMPEL_GELB_PCT
    assert snap["config"]["rot_pct"] == config.AMPEL_ROT_PCT


def test_event_log_hat_je_wechsel_eine_zeile(svc):
    tid = svc.ingest_bon("TISCH 6  19:00\n2x  1  Gyros\n")
    # boniert + gang_gestartet(Hauptgang)
    rows = db.events_for(svc.conn, "ticket", tid)
    typen = [r["typ"] for r in rows]
    assert "boniert" in typen
    assert "gang_gestartet" in typen
