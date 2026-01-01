import { defineConfig } from 'vite'

// TradeX Frontend Configuration
// Vite dev server: port 3000 (per RULES.md)

export default defineConfig({
  server: {
    port: 3000,
    host: true,
    strictPort: true, // Fail if port 3000 is in use
    open: false       // Don't auto-open browser
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
