import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'THS Pala Pro',
        short_name: 'THS Pala Pro',
        description: 'Technical High School Pala – Learn • Build • Innovate Official Website',
        theme_color: '#000000',
        icons: [
          {
            src: '/mobile.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/Desktop.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
