import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'

import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  base: "/mtg-collectron/",
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/mtg-collectron/sets': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      '/mtg-collectron/card': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      '/mtg-collectron/auth': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
