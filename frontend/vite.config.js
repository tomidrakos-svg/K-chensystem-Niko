import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Im Dev-Modus (npm run dev, Port 5173) werden WebSocket und Dev-Endpunkte
// an das Backend (Port 8000) weitergereicht. Im Betrieb liefert das Backend
// den fertigen Build selbst aus, dann greift der Proxy nicht.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/ws': { target: 'ws://localhost:8000', ws: true },
      '/dev': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
