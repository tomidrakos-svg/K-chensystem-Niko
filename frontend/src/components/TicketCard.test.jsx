import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import TicketCard from './TicketCard.jsx'

const cfg = { gelb_pct: 0.72, rot_pct: 1.0 }

function ticket(extra = {}) {
  return {
    id: 1, tisch: '8', bon_uhrzeit: '19:00', created_at: '2026-07-16T19:00:00Z',
    gaenge: [{
      gang: 'Hauptgang', status: 'laufend', gestartet_at: '2026-07-16T19:00:00Z',
      erwartet_min: 10, items: [{ id: 1, menge: 1, name: 'Gyros', fertig: false }],
    }],
    ...extra,
  }
}

describe('TicketCard', () => {
  it('überfälliges Ticket bekommt die Rot-Flut-Klasse', () => {
    const now = Date.parse('2026-07-16T19:11:00Z') // 110% -> rot
    const { container } = render(
      <TicketCard ticket={ticket()} config={cfg} nowMs={now}
        onItemFertig={() => {}} onHauptgangStart={() => {}} />
    )
    expect(container.querySelector('.karte').className).toContain('karte-rot')
    expect(screen.getByText('8')).toBeInTheDocument()   // Tischnummer
  })

  it('frisches Ticket ist neutral', () => {
    const now = Date.parse('2026-07-16T19:02:00Z') // 20%
    const { container } = render(
      <TicketCard ticket={ticket()} config={cfg} nowMs={now}
        onItemFertig={() => {}} onHauptgangStart={() => {}} />
    )
    expect(container.querySelector('.karte').className).toContain('karte-neutral')
  })
})
