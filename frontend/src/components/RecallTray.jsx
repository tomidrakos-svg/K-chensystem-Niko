import React from 'react'

// Zurückholen-Ablage am unteren Rand: die letzten abgeschlossenen Tickets,
// antippen holt sie zurück (Handoff §7, "Recall").
export default function RecallTray({ recall, onZurueckholen }) {
  return (
    <footer className="recall">
      <span className="recall-label">Zurückholen</span>
      <div className="recall-liste">
        {recall.length === 0 && <span className="recall-leer">—</span>}
        {recall.map((t) => (
          <button key={t.id} className="recall-chip" onClick={() => onZurueckholen(t.id)}>
            Tisch {t.tisch}
          </button>
        ))}
      </div>
    </footer>
  )
}
