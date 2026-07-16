import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import GangGroup from './GangGroup.jsx'

const cfg = { gelb_pct: 0.72, rot_pct: 1.0 }
const noop = () => {}

describe('GangGroup', () => {
  it('geparkter Gang: HOLD-Badge, Fortschritt und Start-Button', () => {
    const gang = {
      gang: 'Hauptgang', status: 'geparkt', gestartet_at: null, erwartet_min: 12,
      items: [
        { id: 1, menge: 2, name: 'Gyros', fertig: false },
        { id: 2, menge: 1, name: 'Bifteki', fertig: false },
      ],
    }
    const { container } = render(
      <GangGroup gang={gang} config={cfg} nowMs={Date.parse('2026-07-16T19:00:00Z')}
        onItemFertig={noop} onHauptgangStart={noop}
        showStart startLabel="Hauptgang starten" />
    )
    expect(screen.getByText('Wartet')).toBeInTheDocument()
    expect(screen.getByText('0/2')).toBeInTheDocument()
    expect(screen.getByText('Hauptgang starten')).toBeInTheDocument()
    // geparkte Items sind gesperrt
    expect(container.querySelector('.item')).toBeDisabled()
  })

  it('laufender Gang: Uhr statt Wartet, Zeitleiste sichtbar, Fortschritt zählt', () => {
    const gang = {
      gang: 'Vorspeise', status: 'laufend', gestartet_at: '2026-07-16T19:00:00Z',
      erwartet_min: 4,
      items: [
        { id: 1, menge: 1, name: 'Hühnersuppe', fertig: true },
        { id: 2, menge: 1, name: 'Saganaki', fertig: false },
      ],
    }
    const { container } = render(
      <GangGroup gang={gang} config={cfg} nowMs={Date.parse('2026-07-16T19:01:00Z')}
        onItemFertig={noop} onHauptgangStart={noop} showStart={false} startLabel="" />
    )
    expect(screen.queryByText('Wartet')).toBeNull()
    expect(screen.getByText('1/2')).toBeInTheDocument()
    expect(container.textContent).toContain('1:00')            // laufende Uhr
    expect(container.querySelector('.timeline')).toBeTruthy()
  })
})
