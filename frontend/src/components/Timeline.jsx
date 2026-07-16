import React from 'react'

// Füllende Zeitleiste unter dem Gang-Label (Handoff §6/§7). Breite = Anteil der
// verstrichenen an der erwarteten Zeit; Farbe = Ampelstufe.
export default function Timeline({ pct, level }) {
  const width = Math.min(Math.max(pct, 0), 1) * 100
  return (
    <div className={`timeline timeline-${level}`}>
      <div className="timeline-fill" style={{ width: `${width}%` }} />
    </div>
  )
}
