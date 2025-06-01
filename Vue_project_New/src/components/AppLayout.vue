<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-container">
        <div class="logo-section">
          <router-link to="/" class="logo">
            <div class="logo-icon">AI</div>
            <span class="logo-text">智能教育平台</span>
          </router-link>
        </div>
        
        <nav class="app-nav">
          <!-- 通用导航 -->
          <router-link to="/" class="nav-item" active-class="active">首页</router-link>
          
          <!-- 教师导航 -->
          <template v-if="userStore.isTeacher">
            <router-link to="/course-management" class="nav-item" active-class="active">课程管理</router-link>
            <router-link to="/student-management" class="nav-item" active-class="active">学生管理</router-link>
            <router-link to="/data-statistics" class="nav-item" active-class="active">数据统计</router-link>
          </template>
          
          <!-- 学生导航 -->
          <template v-if="userStore.isStudent">
            <router-link to="/courses" class="nav-item" active-class="active">课程列表</router-link>
            <router-link to="/chat-history" class="nav-item" active-class="active">答题记录</router-link>
            <router-link to="/level-analysis" class="nav-item" active-class="active">统计分析</router-link>
          </template>
        </nav>
        
        <div class="user-actions">
          <el-dropdown trigger="click">
            <div class="user-info">
              <div class="avatar">{{ userStore.username?.charAt(0).toUpperCase() }}</div>
              <div class="user-text">
                <span class="username">{{ userStore.username }}</span>
                <span class="user-role">({{ userStore.currentUser?.role || '未知角色' }})</span>
              </div>
              <span class="dropdown-icon">
                <el-icon><ArrowDown /></el-icon>
              </span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <router-link to="/profile" class="dropdown-link">个人中心</router-link>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 调试信息 -->
      <!-- <div class="debug-info">
        <p>用户ID: {{ userStore.userId }}</p>
        <p>用户名: {{ userStore.username }}</p>
        <p>角色: {{ userStore.currentUser?.role }}</p>
        <p>isTeacher: {{ userStore.isTeacher }}</p>
        <p>isStudent: {{ userStore.isStudent }}</p>
      </div> -->
    </header>
    
    <main class="app-main">
      <div class="main-container">
        <slot></slot>
      </div>
    </main>
    
    <footer class="app-footer">
      <div class="footer-container">

      </div>
    </footer>
  </div>
</template>

<script setup>
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = async () => {
  try {
    const result = await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    if (result === 'confirm') {
      const logoutResult = await userStore.logout()
      if (logoutResult.success) {
        ElMessage.success('退出成功')
        router.push('/login')
      } else {
        ElMessage.error(logoutResult.message || '退出失败')
      }
    }
  } catch (e) {
    // 用户取消操作
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部样式 */
.app-header {
  height: var(--header-height);
  background-color: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

.header-container {
  max-width: 1200px;
  height: 100%;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 4px 10px rgba(45, 90, 241, 0.2);
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-left: 10px;
}

/* 导航样式 */
.app-nav {
  display: flex;
  gap: 30px;
}

.nav-item {
  font-size: 15px;
  color: var(--text-regular);
  text-decoration: none;
  padding: 8px 0;
  position: relative;
  transition: color 0.3s;
  font-weight: 500;
}

.nav-item:hover {
  color: var(--primary-color);
}

.nav-item.active {
  color: var(--primary-color);
  font-weight: 600;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: var(--primary-color);
  border-radius: 3px;
}

/* 用户区域样式 */
.user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 40px;
  transition: background-color 0.3s;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(45, 90, 241, 0.2);
}

.username {
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 500;
}

.user-role {
  font-size: 12px;
  color: #909399;
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-regular);
  margin-left: 4px;
}

.dropdown-link {
  display: block;
  width: 100%;
  color: inherit;
  text-decoration: none;
}

/* 主内容区域 */
.app-main {
  flex: 1;
  padding: 24px 0;
  background-color: var(--bg-color);
}

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 页脚样式 */
.app-footer {
  background-color: #fff;
  padding: 40px 0 20px;
  border-top: 1px solid var(--border-color);
  margin-top: 40px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.footer-logo {
  display: flex;
  align-items: center;
}

.footer-desc {
  max-width: 400px;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

.footer-links-container {
  display: flex;
  gap: 80px;
  margin-bottom: 40px;
}

.footer-links-group {
  display: flex;
  flex-direction: column;
}

.footer-links-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.footer-link:hover {
  color: var(--primary-color);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.copyright {
  color: var(--text-secondary);
  font-size: 13px;
}

.footer-extra-links {
  display: flex;
  gap: 20px;
}

.footer-extra-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.3s;
}

.footer-extra-link:hover {
  color: var(--primary-color);
}

/* 响应式调整 */
@media (max-width: 991px) {
  .footer-links-container {
    gap: 40px;
  }
}

@media (max-width: 768px) {
  .app-nav {
    display: none;
  }
  
  .footer-links-container {
    flex-direction: column;
    gap: 30px;
  }
  
  .footer-bottom {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
}

/* 调试信息 */
.debug-info {
  position: fixed;
  top: var(--header-height);
  right: 0;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 10px;
  border-radius: 0 0 0 8px;
  font-size: 12px;
  z-index: 999;
}

.debug-info p {
  margin: 5px 0;
}
</style> 