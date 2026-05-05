import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/leads': 'http://localhost:8000',
      '/calls': 'http://localhost:8000',
      '/dashboard': 'http://localhost:8000',
      '/webhooks': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
});
