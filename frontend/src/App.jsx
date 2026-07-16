import React, { useEffect, useState } from 'react'
import { useKds, useTick } from './ws.js'
import TicketCard from './components/TicketCard.jsx'
import RecallTray from './components/RecallTray.jsx'

export default function App() {
  const kds = useKds()
  useTick(1000) // Uhren/Ampeln jede Sekunde neu zeichnen
  const nowMs = kds.serverNow()
  const { tickets, recall, config } = kds.snapshot

  // Hell/Dunkel-Umschaltung (Standard: Dunkel = Küchen-Standard), Wahl gemerkt.
  const [theme, setTheme] = useState(
    () => localStorage.getItem('kds-theme') || 'dark'
  )
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('kds-theme', theme)
  }, [theme])

  return (
    <div className="app">
      <header className="kopfzeile">
        <span className="titel">Küche</span>
        <div className="kopf-rechts">
          <span className={`verbindung ${kds.connected ? 'ok' : 'weg'}`}>
            {kds.connected ? 'live' : 'getrennt …'}
          </span>
          <button
            className="theme-toggle"
            onClick={() => setTheme((t) => (t === 'light' ? 'dark' : 'light'))}
            aria-label="Hell oder Dunkel umschalten"
          >
            {theme === 'light' ? '☾ Dunkel' : '☀ Hell'}
          </button>
        </div>
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
