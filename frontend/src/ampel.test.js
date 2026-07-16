import { describe, it, expect } from 'vitest'
import { ampelState, schlimmsteAmpel, mmss, alterMin } from './ampel.js'

const cfg = { gelb_pct: 0.72, rot_pct: 1.0 }
const START = '2026-07-16T19:00:00Z'
const startMs = Date.parse(START)
const lauf = (min, extra = {}) => ({
  gang: 'Hauptgang', status: 'laufend', gestartet_at: START,
  erwartet_min: min, items: [], ...extra,
})

describe('ampelState', () => {
  it('geparkt ohne Start', () => {
    const g = { status: 'geparkt', gestartet_at: null, erwartet_min: 10, items: [] }
    expect(ampelState(g, cfg, startMs).level).toBe('geparkt')
  })

  it('Schwellen neutral -> gelb (72%) -> rot (100%)', () => {
    expect(ampelState(lauf(10), cfg, startMs + 5 * 60000).level).toBe('neutral') // 50%
    expect(ampelState(lauf(10), cfg, startMs + 8 * 60000).level).toBe('gelb')    // 80%
    expect(ampelState(lauf(10), cfg, startMs + 11 * 60000).level).toBe('rot')    // 110%
  })

  it('fertiger Gang friert die Uhr auf fertig_at ein (Regression Uhr-Freeze)', () => {
    const g = {
      status: 'fertig', gestartet_at: START, fertig_at: '2026-07-16T19:07:00Z',
      erwartet_min: 10, items: [],
    }
    const vielSpaeter = Date.parse('2026-07-16T19:30:00Z')
    const r = ampelState(g, cfg, vielSpaeter)
    expect(r.level).toBe('fertig')
    expect(Math.round(r.elapsedSec)).toBe(420) // 7 min eingefroren, NICHT 30 min
  })

  it('fertig ohne fertig_at nutzt jetzt (Fallback)', () => {
    const g = { status: 'fertig', gestartet_at: START, fertig_at: null, erwartet_min: 10, items: [] }
    const now = Date.parse('2026-07-16T19:05:00Z')
    expect(Math.round(ampelState(g, cfg, now).elapsedSec)).toBe(300)
  })
})

describe('ampelState — Minuten-Modus', () => {
  const cfgMin = { modus: 'minuten', gelb_min: 8, rot_min: 12 }
  const g = (extra = {}) => ({
    gang: 'Hauptgang', status: 'laufend', gestartet_at: START,
    erwartet_min: 999, items: [], ...extra, // erwartet_min wird im Minuten-Modus ignoriert
  })
  it('nutzt absolute Minuten statt Prozent', () => {
    expect(ampelState(g(), cfgMin, startMs + 5 * 60000).level).toBe('neutral')  // <8
    expect(ampelState(g(), cfgMin, startMs + 9 * 60000).level).toBe('gelb')     // >=8
    expect(ampelState(g(), cfgMin, startMs + 13 * 60000).level).toBe('rot')     // >=12
  })
  it('friert auch im Minuten-Modus ein', () => {
    const done = { ...g(), status: 'fertig', fertig_at: '2026-07-16T19:06:00Z' }
    const r = ampelState(done, cfgMin, Date.parse('2026-07-16T20:00:00Z'))
    expect(r.level).toBe('fertig')
    expect(Math.round(r.elapsedSec)).toBe(360)
  })
})

describe('schlimmsteAmpel', () => {
  it('nimmt den dringlichsten Gang der Karte', () => {
    const gaenge = [
      { status: 'fertig', gestartet_at: START, fertig_at: START, erwartet_min: 10, items: [] },
      lauf(10), // bei +11min rot
    ]
    expect(schlimmsteAmpel(gaenge, cfg, startMs + 11 * 60000)).toBe('rot')
  })

  it('neutral wenn alle im grünen Bereich', () => {
    expect(schlimmsteAmpel([lauf(10)], cfg, startMs + 2 * 60000)).toBe('neutral')
  })
})

describe('Formatierung', () => {
  it('mmss', () => {
    expect(mmss(75)).toBe('1:15')
    expect(mmss(5)).toBe('0:05')
  })
  it('alterMin', () => {
    expect(alterMin(START, Date.parse('2026-07-16T19:03:30Z'))).toBe(3)
  })
})
