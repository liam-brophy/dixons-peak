import { defineConfig } from 'vite';

export default defineConfig({
  // Base path for deployment
  base: './',
  
  // Specify the build output directory
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Enable asset inlining to simplify deployment
    assetsInlineLimit: 0,
  },
  
  // Configure the server
  server: {
    host: true,
    port: 3000,
  },
});
