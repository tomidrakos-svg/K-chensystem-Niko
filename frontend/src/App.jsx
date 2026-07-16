import React from 'react'
import { useKds, useTick } from './ws.js'
import TicketCard from './components/TicketCard.jsx'
import RecallTray from './components/RecallTray.jsx'

export default function App() {
  const kds = useKds()
  useTick(1000) // Uhren/Ampeln jede Sekunde neu zeichnen
  const nowMs = kds.serverNow()
  const { tickets, recall, config } = kds.snapshot

  return (
    <div className="app">
      <header className="kopfzeile">
        <span className="titel">Küche</span>
        <span className={`verbindung ${kds.connected ? 'ok' : 'weg'}`}>
          {kds.connected ? 'live' : 'getrennt …'}
        </span>
      </header>

      <main className="raster">
        {tickets.length === 0 && (
          <div className="leerhinweis">Keine offenen Tische</div>
        )}
        {tickets.map((t) => (
          <TicketCard
            key={t.id}
            ticket={t}
            config={config}
            nowMs={nowMs}
            onItemFertig={kds.itemFertig}
            onHauptgangStart={kds.hauptgangStart}
          />
        ))}
      </main>

      <RecallTray recall={recall} onZurueckholen={kds.zurueckholen} />
    </div>
  )
}
