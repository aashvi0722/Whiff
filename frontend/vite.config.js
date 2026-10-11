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
        theme_color: '#f5f1ff',
        background_color: '#f5f1ff',
        display: 'standalone',
           icons: [
     { src: '/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
     { src: '/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
     { src: '/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
   ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
      },
    }),
  ],
})