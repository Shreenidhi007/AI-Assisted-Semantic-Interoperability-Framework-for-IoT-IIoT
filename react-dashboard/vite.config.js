import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/semantic-react/',
  server: {
    port: 8502,
    host: '0.0.0.0',
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8008',
        changeOrigin: true,
      }
    }
  },
  preview: {
    port: 8502,
    host: '0.0.0.0'
  }
})

