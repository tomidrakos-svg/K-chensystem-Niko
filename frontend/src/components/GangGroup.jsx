import React from 'react'
import { ampelState, mmss } from '../ampel.js'
import Timeline from './Timeline.jsx'
import GarstufeBadge from './GarstufeBadge.jsx'

// Eine Gang-Gruppe mit eigener Uhr, Zeitleiste und Item-Liste. Geparkter
// Hauptgang zeigt den einzigen farbigen Button "Hauptgang starten" (Handoff §7).
export default function GangGroup({ gang, config, nowMs, onItemFertig, onHauptgangStart }) {
  const { level, pct, elapsedSec } = ampelState(gang, config, nowMs)
  const geparkt = gang.status === 'geparkt'
  const zeigeStartButton = geparkt && gang.gang === 'Hauptgang'

  return (
    <div className={`gang ${geparkt ? 'gang-geparkt' : ''}`}>
      <div className="gang-kopf">
        <span className="gang-label">{gang.gang}</span>
        <span className="gang-uhr">
          {geparkt ? 'wartet' : mmss(elapsedSec)}
          {!geparkt && <span className="gang-erwartet"> / {gang.erwartet_min}:00</span>}
        </span>
      </div>

      {!geparkt && <Timeline pct={pct} level={level} />}

      <ul className="items">
        {gang.items.map((it) => (
          <li key={it.id}>
            <button
              className={`item ${it.fertig ? 'item-fertig' : ''} ${geparkt ? 'item-gesperrt' : ''}`}
              onClick={() => !geparkt && !it.fertig && onItemFertig(it.id)}
              disabled={geparkt}
            >
              <span className="item-menge">{it.menge}×</span>
              <span className="item-name">
                {it.name}
                {it.unbekannt && <span className="badge-unbekannt">unbekannt</span>}
                {it.ambiguous && !it.unbekannt && <span className="badge-ambig">nr?</span>}
              </span>
              <GarstufeBadge garstufe={it.garstufe} />
            </button>
            {it.notiz && <div className="item-notiz">» {it.notiz}</div>}
          </li>
        ))}
      </ul>

      {zeigeStartButton && (
        <button className="btn-hauptgang" onClick={() => onHauptgangStart()}>
          Hauptgang starten
        </button>
      )}
    </div>
  )
}
