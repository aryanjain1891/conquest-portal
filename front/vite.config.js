import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import websiteOverlay from 'website-overlay/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), websiteOverlay()],
})
