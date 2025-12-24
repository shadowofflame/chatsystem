import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // SSE 流式端点 - 特殊配置
      '/api/chat/stream': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        timeout: 0,           // 无超时
        proxyTimeout: 0,      // 无代理超时
        // 关键：配置流式响应
        configure: (proxy, options) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 禁用缓冲，实现实时流
            proxyRes.headers['cache-control'] = 'no-cache';
            proxyRes.headers['x-accel-buffering'] = 'no';
          });
        }
      },
      // 其他 API
      '/api': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        timeout: 300000,      // 5分钟代理超时
        proxyTimeout: 300000,
      }
    }
  }
})
