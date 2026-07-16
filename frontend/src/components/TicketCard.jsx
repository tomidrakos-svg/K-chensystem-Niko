import React from 'react'
import { alterMin, schlimmsteAmpel } from '../ampel.js'
import GangGroup from './GangGroup.jsx'

// Eine Ticket-Karte: Tischnummer riesig, Bonzeit + Alter klein, darunter die
// Gang-Gruppen (Handoff §7). Kartenrand = dringlichster Gang.
export default function TicketCard({ ticket, config, nowMs, onItemFertig, onHauptgangStart }) {
  const rand = schlimmsteAmpel(ticket.gaenge, config, nowMs)
  const alter = alterMin(ticket.created_at, nowMs)
  // Start-Button am ersten geparkten Nicht-Vorspeise-Gang (meist Hauptgang;
  // fällt es weg, kann auch ein geparktes Dessert gestartet werden — sonst bliebe
  // es unstartbar). Die Aktion startet alle geparkten Nicht-Vorspeise-Gänge.
  const startAnker = ticket.gaenge.find(
    (g) => g.status === 'geparkt' && g.gang !== 'Vorspeise'
  )

  return (
    <div className={`karte karte-${rand}`}>
      <div className="karte-kopf">
        <span className="tisch">{ticket.tisch}</span>
        <span className="karte-meta">
          <span className="bonzeit">{ticket.bon_uhrzeit || '—'}</span>
          <span className="alter">vor {alter} min</span>
        </span>
      </div>
      {ticket.gaenge.map((g) => (
        <GangGroup
          key={g.gang}
          gang={g}
          config={config}
          nowMs={nowMs}
          onItemFertig={onItemFertig}
          onHauptgangStart={() => onHauptgangStart(ticket.id)}
          showStart={startAnker && g.gang === startAnker.gang}
          startLabel={startAnker && startAnker.gang === 'Hauptgang' ? 'Hauptgang starten' : 'Dessert starten'}
        />
      ))}
    </div>
  )
}
