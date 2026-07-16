import { useCallback, useEffect, useRef, useState } from 'react'

const EMPTY = {
  type: 'snapshot',
  tickets: [],
  recall: [],
  config: { gelb_pct: 0.72, rot_pct: 1.0 },
  server_now: null,
}

// Verbindet zum Backend-WebSocket, haelt den letzten Snapshot und bietet die
// drei Aktionen an. Bei Verbindungsabbruch wird automatisch neu verbunden
// (Handoff §1: ein Ausfall darf die Kueche nie stoppen).
export function useKds() {
  const [snapshot, setSnapshot] = useState(EMPTY)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const offsetRef = useRef(0) // clientNow - serverNow (ms), fuer Uhr-Synchronisation

  useEffect(() => {
    let closed = false
    let reconnectTimer = null

    function connect() {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws'
      const ws = new WebSocket(`${proto}://${location.host}/ws`)
      wsRef.current = ws
      ws.onopen = () => setConnected(true)
      ws.onmessage = (ev) => {
        const data = JSON.parse(ev.data)
        if (data.server_now) {
          offsetRef.current = Date.now() - Date.parse(data.server_now)
        }
        setSnapshot(data)
      }
      ws.onclose = () => {
        setConnected(false)
        if (!closed) reconnectTimer = setTimeout(connect, 1500)
      }
      ws.onerror = () => ws.close()
    }

    connect()
    return () => {
      closed = true
      if (reconnectTimer) clearTimeout(reconnectTimer)
      wsRef.current?.close()
    }
  }, [])

  const send = useCallback((msg) => {
    const ws = wsRef.current
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg))
  }, [])

  const serverNow = useCallback(() => Date.now() - offsetRef.current, [])

  return {
    snapshot,
    connected,
    serverNow,
    itemFertig: (id) => send({ type: 'item_fertig', item_id: id }),
    hauptgangStart: (id) => send({ type: 'hauptgang_start', ticket_id: id }),
    zurueckholen: (id) => send({ type: 'zurueckholen', ticket_id: id }),
  }
}

// Erzwingt einen Re-Render im Sekundentakt, damit Uhren/Ampeln live laufen.
export function useTick(ms = 1000) {
  const [, setN] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setN((n) => n + 1), ms)
    return () => clearInterval(t)
  }, [ms])
}
