import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',  // CloudFront serves from root
  build: {
    assetsDir: 'assets',  // Explicit assets directory
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor code for better caching
          react: ['react', 'react-dom', 'react-router-dom'],
          monaco: ['@monaco-editor/react', 'monaco-editor'],
        },
      },
    },
  },
  server: {
    proxy: {
      // Proxy API routes to local backend during development
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
