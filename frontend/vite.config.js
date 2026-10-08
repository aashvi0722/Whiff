import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'], // Caches your local assets
      manifest: {
        name: "Whiff",
        short_name: "Whiff",
        description: "Know when the smoke is coming.",
        theme_color: "#0f172a",
        background_color: "#09090b",
        display: "standalone",
        icons: [
          {
            src: "/favicon.svg",
            sizes: "any",
            type: "image/svg+xml",
            purpose: "any maskable"
          }
        ]
      },
      workbox: {
        // Automatically caches your JS, CSS, and HTML for offline use
        globPatterns: ['**/*.{js,css,html,ico,png,svg}']
      }
    })
  ]
})