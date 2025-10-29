import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // 配置路径别名
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@styles': resolve(__dirname, 'src/styles'),
    },
  },

  // 开发服务器配置
  server: {
    port: 9999,
    host: 'localhost',
    strictPort: false,
    proxy: {
      // API代理到后端服务
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      // WebSocket代理
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },

  // 构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
      output: {
        manualChunks: {
          // 将React相关库打包在一起
          'react-vendor': ['react', 'react-dom'],
          // 将UI库打包在一起
          'ui-vendor': ['antd', '@ant-design/icons'],
          // 将图表库打包在一起
          'chart-vendor': ['echarts', 'recharts', 'lightweight-charts'],
          // 将工具库打包在一起
          'utils-vendor': ['lodash-es', 'dayjs', 'axios'],
        },
      },
    },
    // 设置chunk大小警告的限制
    chunkSizeWarningLimit: 1000,
  },

  // 预览服务器配置
  preview: {
    port: 4173,
    host: 'localhost',
    strictPort: true,
  },

  // 依赖优化
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'antd',
      '@ant-design/icons',
      'axios',
      'dayjs',
      'echarts',
      'recharts',
      'socket.io-client',
      'zustand',
      '@tanstack/react-query',
    ],
  },

  // CSS配置
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@styles/variables.scss";`,
      },
    },
  },

  // 环境变量配置
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
})