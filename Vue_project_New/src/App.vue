<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 当前激活的导航项
const activeLink = ref('/')

// 判断是否为登录页
const isLoginPage = computed(() => route.path === '/login')

// 监听路由变化，更新激活的导航项
watch(() => route.path, (path) => {
  activeLink.value = path
})

// 退出登录
const logout = async () => {
  const result = await userStore.logout()
  if (result.success) {
    ElMessage.success('退出成功')
    router.push('/login')
  } else {
    ElMessage.error(result.message)
  }
}

// 组件挂载时检查登录状态
onMounted(async () => {
  if (!isLoginPage.value) {
    const isLoggedIn = await userStore.checkAuth()
    if (!isLoggedIn) {
      router.push('/login')
    }
  }
})
</script>

<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition name="fade-transform" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
:root {
  --primary-color: #3a7bd5;
  --primary-gradient: linear-gradient(to right, #3a7bd5, #00d2ff);
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #f5222d;
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;
  --border-color: #e4e7ed;
  --bg-color: #f5f7fa;
  --header-height: 60px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-primary);
  background-color: var(--bg-color);
  font-size: 14px;
  line-height: 1.5;
  overflow-x: hidden; /* 防止水平滚动 */
}

#app {
  min-height: 100vh;
  position: relative;
}

.page-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeIn 0.8s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: 500;
  color: var(--text-primary);
}

.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05) !important;
  border: none !important;
  overflow: hidden;
  transition: all 0.3s;
}

.el-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1) !important;
}

.el-button {
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
  position: relative;
  overflow: hidden;
}

.el-button--primary {
  background: var(--primary-gradient) !important;
  border-color: var(--primary-color) !important;
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 123, 213, 0.4);
}

.el-button--primary:active {
  transform: translateY(0);
}

.el-button--success {
  background-color: var(--success-color) !important;
  border-color: var(--success-color) !important;
}

.el-button--warning {
  background-color: var(--warning-color) !important;
  border-color: var(--warning-color) !important;
}

.el-button--danger {
  background-color: var(--danger-color) !important;
  border-color: var(--danger-color) !important;
}

/* 动画效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.slide-fade-enter-from, .slide-fade-leave-to {
  transform: translateX(30px);
  opacity: 0;
}

/* 新增过渡动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.5s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

/* 元素悬浮效果 */
.hover-float {
  transition: transform 0.3s ease;
}

.hover-float:hover {
  transform: translateY(-5px);
}

/* 脉冲动画 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(58, 123, 213, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(58, 123, 213, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(58, 123, 213, 0);
  }
}

.pulse {
  animation: pulse 2s infinite;
}

/* 更平滑的滚动体验 */
html {
  scroll-behavior: smooth;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
