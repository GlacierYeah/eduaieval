import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // 添加语音识别工具别名
      '@voice-utils': path.resolve(__dirname, './src/voice-utils')
    }
  },
  server: {
    // 设置静态资源路径
    fs: {
      // 允许访问上级目录
      allow: ['..']
    },
    // --- 添加代理配置 ---
    proxy: {
      // 规则：匹配所有以 /static 开头的请求路径
      '/static': {
        // 目标服务器地址：这里需要填写你后端服务器的实际地址和端口
        // 例如，如果你的后端运行在 http://localhost:8000
        target: 'http://127.0.0.1:5000', // <--- 请将这里替换成你的后端地址!
        
        // 重要：更改请求头中的 Origin 字段，设置为目标地址的源
        // 这对于避免后端服务器基于 Origin 的安全检查（例如 CORS）是必要的
        changeOrigin: true, 
        
        // 可选：路径重写
        // 如果后端的静态文件服务路径结构与前端请求的路径不同，可以使用 rewrite
        // 例如，如果后端没有 /static 前缀，你可能需要像这样去掉它：
        // rewrite: (path) => path.replace(/^\/static/, '') 
        // 但根据你的描述，后端路径也是 /static 开头，所以可能不需要 rewrite
      },

      // --- （可选）如果你还有 API 请求需要代理到后端，可以添加类似规则 ---
      '/api': {
         target: 'http://127.0.0.1:5000', // <--- 同样替换成你的后端地址
         changeOrigin: true,
         // 通常 API 路径重写会去掉 /api 前缀
         rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
    // --- 代理配置结束 ---
  },
  // 配置构建选项，确保生产环境也能访问到资源
  build: {
    // ... (build 配置保持不变) ...
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 将语音识别相关代码单独打包
          if (id.includes('voice-utils')) {
            return 'voice-utils';
          }
        }
      }
    }
  }
})
