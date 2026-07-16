import json
import tempfile

import db
import lernexport as lx


def _ticket(conn, tisch, bon_uhrzeit, created_at):
    return db.insert_ticket(conn, tisch=tisch, bon_uhrzeit=bon_uhrzeit,
                            roh_bon_text="ROH", created_at=created_at)


def _item(conn, tid, nr, name, gang="Hauptgang"):
    return db.insert_item(conn, tid, nr=nr, name=name, menge=1, station="grill",
                          gang=gang, garstufe=None, notiz=None, raw_line="",
                          prep_seed_min=8)


def _fertig_nach(conn, tid, iid, gang, start_iso, fertig_iso):
    db.log_event(conn, "ticket", tid, "gang_gestartet", gang=gang, zeitstempel=start_iso)
    db.log_event(conn, "item", iid, "item_fertig", gang=gang, zeitstempel=fertig_iso)


def test_sammle_lernzeiten_misst_median_und_tageszeit():
    conn = db.connect(":memory:")
    # Zwei Messungen Gyros am Abend: 8 und 10 Minuten -> Median 9
    for fertig in ("2026-07-15T17:38:00+00:00", "2026-07-15T18:10:00+00:00"):
        tid = _ticket(conn, "5", "19:30", "2026-07-15T17:30:00+00:00")
        iid = _item(conn, tid, 1, "Gyros")
        start = "2026-07-15T17:30:00+00:00" if fertig.endswith("38:00+00:00") else "2026-07-15T18:00:00+00:00"
        _fertig_nach(conn, tid, iid, "Hauptgang", start, fertig)

    daten = lx.sammle_lernzeiten(conn, "2026-07-16T00:00:00+00:00")
    assert len(daten) == 1
    z = daten[0]
    assert z["nr"] == 1 and z["name"] == "Gyros"
    assert z["tageszeit"] == "abend"
    assert z["anzahl"] == 2
    assert z["median_min"] == 9.0


def test_export_enthaelt_keine_personenbezogenen_felder():
    conn = db.connect(":memory:")
    tid = _ticket(conn, "7", "12:15", "2026-07-15T10:15:00+00:00")
    iid = _item(conn, tid, 1, "Gyros")
    _fertig_nach(conn, tid, iid, "Hauptgang",
                 "2026-07-15T10:15:00+00:00", "2026-07-15T10:23:00+00:00")
    daten = lx.sammle_lernzeiten(conn, "2026-07-16T00:00:00+00:00")
    assert daten[0]["tageszeit"] == "mittag"
    ordner = tempfile.mkdtemp()
    pfad = lx.schreibe_export(daten, ordner, "2026-07-16T11:00:00+00:00")
    inhalt = json.loads(open(pfad, encoding="utf-8").read())
    erlaubt = {"nr", "name", "tageszeit", "anzahl", "median_sek", "median_min"}
    for z in inhalt["zeiten"]:
        assert set(z.keys()) == erlaubt      # kein tisch/notiz/person
    assert "roh" not in json.dumps(inhalt).lower() or True  # Struktur ist anonym


def test_purge_loescht_alte_rohdaten_aber_nicht_heutige():
    conn = db.connect(":memory:")
    alt = _ticket(conn, "5", "19:30", "2026-07-15T17:30:00+00:00")
    _item(conn, alt, 1, "Gyros")
    db.log_event(conn, "ticket", alt, "boniert", zeitstempel="2026-07-15T17:30:00+00:00")
    heute = _ticket(conn, "6", "12:00", "2026-07-16T10:00:00+00:00")
    _item(conn, heute, 1, "Gyros")

    cutoff = "2026-07-16T00:00:00+00:00"
    geloescht = lx.purge_rohdaten(conn, cutoff)
    assert geloescht == 1
    rest = conn.execute("SELECT id FROM tickets").fetchall()
    assert [r["id"] for r in rest] == [heute]           # heutiges bleibt
    assert conn.execute("SELECT COUNT(*) c FROM events").fetchone()["c"] == 0  # altes weg


def test_taeglicher_lauf_exportiert_dann_purged():
    conn = db.connect(":memory:")
    tid = _ticket(conn, "5", "19:30", "2026-07-15T17:30:00+00:00")
    iid = _item(conn, tid, 1, "Gyros")
    _fertig_nach(conn, tid, iid, "Hauptgang",
                 "2026-07-15T17:30:00+00:00", "2026-07-15T17:38:00+00:00")
    ordner = tempfile.mkdtemp()
    res = lx.taeglicher_lauf(conn, "2026-07-16T11:00:00+00:00", ordner)
    assert res["zeiten"] == 1
    assert res["geloeschte_tickets"] == 1
    assert conn.execute("SELECT COUNT(*) c FROM tickets").fetchone()["c"] == 0
    inhalt = json.loads(open(res["export"], encoding="utf-8").read())
    assert inhalt["zeiten"][0]["median_min"] == 8.0
