import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import RecallTray from './RecallTray.jsx'

describe('RecallTray', () => {
  it('leere Ablage zeigt einen Strich', () => {
    render(<RecallTray recall={[]} onZurueckholen={() => {}} />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('zeigt Chips und ruft beim Klick den Zurückholen-Handler mit der id', () => {
    const calls = []
    render(
      <RecallTray
        recall={[{ id: 5, tisch: 9 }, { id: 6, tisch: 14 }]}
        onZurueckholen={(id) => calls.push(id)}
      />
    )
    expect(screen.getByText('Tisch 9')).toBeInTheDocument()
    expect(screen.getByText('Tisch 14')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Tisch 9'))
    expect(calls).toEqual([5])
  })
})
