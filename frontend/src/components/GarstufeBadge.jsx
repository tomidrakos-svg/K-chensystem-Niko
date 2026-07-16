import React from 'react'

// Garstufe als Badge direkt am Gericht (Handoff §6).
export default function GarstufeBadge({ garstufe }) {
  if (!garstufe) return null
  return <span className="garstufe-badge">{garstufe}</span>
}
