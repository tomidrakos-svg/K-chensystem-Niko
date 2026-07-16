// Ampel-Logik (Handoff §6): eine Uhr pro Gang-Gruppe. Erwartete Zeit = max
// prep_seed_min der Items. neutral -> gelb ab gelb_pct -> rot ab rot_pct.
// Die Schwellen kommen aus dem Server-Snapshot (config), nicht hartcodiert.

export function ampelState(gang, config, nowMs) {
  if (gang.status === 'geparkt' || !gang.gestartet_at) {
    return { level: 'geparkt', pct: 0, elapsedSec: 0 }
  }
  const startMs = Date.parse(gang.gestartet_at)
  // Fertiger Gang: Uhr auf dem Abschlusszeitpunkt einfrieren (nicht weiterlaufen).
  const endMs = gang.status === 'fertig' && gang.fertig_at
    ? Date.parse(gang.fertig_at)
    : nowMs
  const elapsedSec = Math.max(0, (endMs - startMs) / 1000)
  const erwartetSec = (gang.erwartet_min || 0) * 60
  const pct = erwartetSec > 0 ? elapsedSec / erwartetSec : 0
  if (gang.status === 'fertig') {
    return { level: 'fertig', pct: Math.min(pct, 1), elapsedSec }
  }
  let level = 'neutral'
  if (pct >= config.rot_pct) level = 'rot'
  else if (pct >= config.gelb_pct) level = 'gelb'
  return { level, pct, elapsedSec }
}

const RANK = { fertig: 0, geparkt: 0, neutral: 1, gelb: 2, rot: 3 }

// Kartenrand = dringlichster Gang der Karte.
export function schlimmsteAmpel(gaenge, config, nowMs) {
  let worst = 'neutral'
  for (const g of gaenge) {
    const { level } = ampelState(g, config, nowMs)
    if (RANK[level] > RANK[worst]) worst = level
  }
  return worst
}

export function mmss(sec) {
  const s = Math.floor(sec)
  const m = Math.floor(s / 60)
  return `${m}:${String(s % 60).padStart(2, '0')}`
}

export function alterMin(createdAtIso, nowMs) {
  const min = Math.floor((nowMs - Date.parse(createdAtIso)) / 60000)
  return min
}
