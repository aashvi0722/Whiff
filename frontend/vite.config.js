import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  resolve: {
    alias: {
      // the shared data contract lives in the repo's /contract folder (outside /frontend)
      '@contract': fileURLToPath(new URL('../contract', import.meta.url)),
    },
  },
  server: {
    fs: { allow: ['..'] }, // lets Vite read files from the folder above /frontend
  },
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: 'Whiff',
        short_name: 'Whiff',
        description: 'Know when the smoke is coming.',
        theme_color: '#dff7f2',
        background_color: '#e2f8f4',
        display: 'standalone',
        icons: [
          {
            src: '/favicon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
      },
    }),
  ],
})