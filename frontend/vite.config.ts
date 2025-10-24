import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 移除console.log
        drop_debugger: true, // 移除debugger
      },
    },
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // React 核心
          if (id.includes('react') || id.includes('react-dom')) {
            return 'react-vendor'
          }
          // Ant Design 相关
          if (id.includes('antd') || id.includes('@ant-design')) {
            return 'antd-vendor'
          }
          // 图表库
          if (id.includes('echarts')) {
            return 'charts-vendor'
          }
          // 工具库
          if (id.includes('lodash') || id.includes('dayjs') || id.includes('axios')) {
            return 'utils-vendor'
          }
          // 其他node_modules
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      }
    },
    // 提高chunk大小警告阈值
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 5173,
    strictPort: true,
    host: '127.0.0.1',
    hmr: {
      overlay: false, // 关闭错误遮罩
    }
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'antd',
      '@ant-design/icons',
      'echarts',
      'echarts-for-react',
      'axios',
      'dayjs',
      'lodash',
    ],
  },
})