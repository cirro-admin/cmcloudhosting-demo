import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// In development Vite serves the UI and proxies /api to Spring Boot, so the
// browser only ever talks to one origin and CORS stays out of the way.
// In production nginx does the same job — see deploy/nginx-java-starter.conf.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.API_TARGET || 'http://127.0.0.1:11001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
