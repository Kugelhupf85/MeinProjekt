import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    
    // =====================================================================================
    // 🌐 SERVER CONFIGURATION - AUS .env
    // =====================================================================================
    server: {
      host: env.VITE_HOST || '0.0.0.0',
      port: parseInt(env.VITE_PORT) || 3000,
      strictPort: env.VITE_STRICT_PORT === 'true',
      
      // =====================================================================================
      // 🔄 PROXY CONFIGURATION - BACKEND API
      // =====================================================================================
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://arcanovi-backend:8000',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('🚨 Proxy error:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('🔄 Sending Request to the Target:', req.method, req.url);
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('✅ Received Response from the Target:', proxyRes.statusCode, req.url);
            });
          },
        },
        '/admin': {
          target: env.VITE_BACKEND_URL || 'http://arcanovi-backend:8000',
          changeOrigin: true,
          secure: false,
        },
        '/static': {
          target: env.VITE_BACKEND_URL || 'http://arcanovi-backend:8000',
          changeOrigin: true,
          secure: false,
        },
        '/media': {
          target: env.VITE_BACKEND_URL || 'http://arcanovi-backend:8000',
          changeOrigin: true,
          secure: false,
        }
      },
      
      // =====================================================================================
      // 🔥 HMR CONFIGURATION - AUS .env
      // =====================================================================================
      hmr: {
        port: parseInt(env.HMR_PORT) || 5005,
        host: env.HMR_CLIENT_HOST || 'localhost',
      }
    },
    
    // =====================================================================================
    // 🏗️ BUILD CONFIGURATION - AUS .env
    // =====================================================================================
    build: {
      outDir: env.VITE_OUT_DIR || 'dist',
      sourcemap: env.VITE_SOURCE_MAP === 'true',
      minify: env.VITE_MINIFY || 'esbuild',
      
      // Rollup options
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
            utils: ['axios', '@tanstack/react-query']
          }
        }
      }
    },
    
    // =====================================================================================
    // 🔧 ENVIRONMENT VARIABLES
    // =====================================================================================
    define: {
      // Make some env variables available to the client
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },
    
    // =====================================================================================
    // 📁 RESOLVE CONFIGURATION
    // =====================================================================================
    resolve: {
      alias: {
        '@': '/src',
        '@components': '/src/components',
        '@pages': '/src/pages',
        '@utils': '/src/utils',
        '@hooks': '/src/hooks',
        '@store': '/src/store',
        '@assets': '/src/assets',
      }
    },
    
    // =====================================================================================
    // 🎨 CSS CONFIGURATION
    // =====================================================================================
    css: {
      postcss: './postcss.config.js',
    }
  }
}) 