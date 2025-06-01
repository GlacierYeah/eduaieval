<template>
  <app-layout>
    <div class="user-profile">
      <div class="animated-background">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
      
      <h1 class="page-title animate__animated animate__fadeInDown">
        <span class="title-icon"><i class="fas fa-user-circle"></i></span>
        个人中心
      </h1>
      
      <el-card class="profile-card animate__animated animate__fadeInUp">
        <el-tabs v-model="activeTab" class="custom-tabs">
          <!-- 基本信息标签页 -->
          <el-tab-pane label="基本信息" name="basic">
            <div class="user-basic-info">
              <div class="avatar-section animate__animated animate__fadeIn animate__delay-1s">
                <div class="avatar-container">
                  <div class="avatar">
                    {{ userStore.username?.charAt(0).toUpperCase() }}
                    <div class="avatar-glow"></div>
                  </div>
                  <div class="avatar-badge">{{ userStore.currentUser?.role || '用户' }}</div>
                </div>
                <div class="username-display">
                  {{ userStore.username || '用户名' }}
                </div>
              </div>
              
              <el-form 
                :model="basicInfo" 
                label-width="100px" 
                class="profile-form animate__animated animate__fadeIn animate__delay-1s"
                ref="basicInfoForm"
              >
                <el-form-item label="用户名">
                  <el-input v-model="basicInfo.username" disabled class="custom-input">
                    <template #prefix>
                      <i class="form-icon fas fa-user"></i>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="用户角色">
                  <el-input v-model="basicInfo.role" disabled class="custom-input">
                    <template #prefix>
                      <i class="form-icon fas fa-user-tag"></i>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="真实姓名">
                  <el-input v-model="basicInfo.realName" placeholder="请输入真实姓名" class="custom-input">
                    <template #prefix>
                      <i class="form-icon fas fa-id-card"></i>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item label="电子邮箱">
                  <el-input v-model="basicInfo.email" placeholder="请输入电子邮箱" class="custom-input">
                    <template #prefix>
                      <i class="form-icon fas fa-envelope"></i>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveBasicInfo" :loading="submitting" class="submit-btn">
                    <i class="fas fa-save"></i> 保存信息
                    <span class="btn-shine"></span>
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
          
          <!-- 密码修改标签页 -->
          <el-tab-pane label="密码修改" name="password">
            <el-form 
              :model="passwordForm" 
              label-width="120px" 
              class="profile-form animate__animated animate__fadeIn animate__delay-1s"
              ref="passwordFormRef"
              :rules="passwordRules"
            >
              <el-form-item label="当前密码" prop="currentPassword">
                <el-input 
                  v-model="passwordForm.currentPassword" 
                  type="password"
                  placeholder="请输入当前密码"
                  show-password
                  class="custom-input"
                >
                  <template #prefix>
                    <i class="form-icon fas fa-lock"></i>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="新密码" prop="newPassword">
                <el-input 
                  v-model="passwordForm.newPassword" 
                  type="password"
                  placeholder="请输入新密码"
                  show-password
                  class="custom-input"
                >
                  <template #prefix>
                    <i class="form-icon fas fa-key"></i>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input 
                  v-model="passwordForm.confirmPassword" 
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password
                  class="custom-input"
                >
                  <template #prefix>
                    <i class="form-icon fas fa-check-double"></i>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="changePassword" :loading="submitting" class="submit-btn">
                  <i class="fas fa-key"></i> 修改密码
                  <span class="btn-shine"></span>
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import AppLayout from '../components/AppLayout.vue'
import axios from 'axios'

const userStore = useUserStore()
const activeTab = ref('basic')
const submitting = ref(false)

// 基本信息表单
const basicInfo = reactive({
  username: userStore.username || '',
  role: userStore.currentUser?.role || '未知角色',
  realName: '',
  email: ''
})

// 密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码表单验证规则
const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const response = await axios.get('/api/current_user')
    if (response.data.logged_in) {
      const userData = response.data.user
      basicInfo.realName = userData.real_name || ''
      basicInfo.email = userData.email || ''
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
}

// 保存基本信息
const saveBasicInfo = async () => {
  submitting.value = true
  try {
    const response = await axios.post('/api/user/update-info', {
      real_name: basicInfo.realName,
      email: basicInfo.email
    })
    
    if (response.data.success) {
      ElMessage.success('个人信息保存成功')
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存个人信息失败', error)
    ElMessage.error('保存个人信息失败')
  } finally {
    submitting.value = false
  }
}

// 修改密码
const passwordFormRef = ref(null)
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const response = await axios.post('/api/user/change-password', {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword
      })
      
      if (response.data.success) {
        ElMessage.success('密码修改成功')
        // 清空表单
        passwordForm.currentPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } else {
        ElMessage.error(response.data.message || '密码修改失败')
      }
    } catch (error) {
      console.error('修改密码失败', error)
      ElMessage.error('修改密码失败')
    } finally {
      submitting.value = false
    }
  })
}

// 加载字体图标
const loadFontAwesome = () => {
  const fontAwesomeLink = document.createElement('link')
  fontAwesomeLink.rel = 'stylesheet'
  fontAwesomeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
  document.head.appendChild(fontAwesomeLink)
}

// 页面加载时获取数据
onMounted(async () => {
  await loadUserInfo()
  loadFontAwesome()
  
  // 设置Animate.css的动画持续时间
  document.documentElement.style.setProperty('--animate-duration', '0.8s')
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

:root {
  --primary-color: #5e72eb;
  --secondary-color: #00d2ff;
  --primary-gradient: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
  --text-primary: #303133;
  --text-secondary: #606266;
  --text-light: #909399;
  --bg-light: #f8f9fa;
  --shadow-sm: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 5px 15px 0 rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 25px 0 rgba(0, 0, 0, 0.1);
}

.user-profile {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px 20px;
  position: relative;
  min-height: calc(100vh - 120px);
  overflow: hidden;
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
}

/* 动态背景效果 */
.animated-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  opacity: 0.5;
}

.shape-1 {
  top: -100px;
  right: -100px;
  width: 300px;
  height: 300px;
  background: rgba(94, 114, 235, 0.1);
  animation: float 20s infinite alternate ease-in-out;
}

.shape-2 {
  bottom: -150px;
  left: -100px;
  width: 400px;
  height: 400px;
  background: rgba(0, 210, 255, 0.1);
  animation: float 25s infinite alternate-reverse ease-in-out;
}

.shape-3 {
  top: 40%;
  left: 30%;
  width: 250px;
  height: 250px;
  background: rgba(138, 43, 226, 0.05);
  animation: pulse 15s infinite alternate ease-in-out;
}

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(30px, -30px) rotate(5deg); }
  100% { transform: translate(-30px, 30px) rotate(-5deg); }
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.4; }
  50% { transform: scale(1.2); opacity: 0.6; }
  100% { transform: scale(0.8); opacity: 0.4; }
}

.page-title {
  font-size: 30px;
  margin-bottom: 30px;
  color: var(--text-primary);
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.title-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 36px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: iconPulse 2s infinite alternate ease-in-out;
}

@keyframes iconPulse {
  0% { transform: scale(1); }
  100% { transform: scale(1.1); }
}

.profile-card {
  border-radius: 20px !important;
  box-shadow: var(--shadow-lg) !important;
  margin-bottom: 30px;
  overflow: hidden;
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8) !important;
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.profile-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg), 0 15px 35px rgba(94, 114, 235, 0.1) !important;
}

/* 自定义标签页样式 */
.custom-tabs :deep(.el-tabs__header) {
  margin-bottom: 25px;
  border-bottom: 1px solid rgba(94, 114, 235, 0.1);
}

.custom-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  padding: 0 20px;
  height: 50px;
  line-height: 50px;
}

.custom-tabs :deep(.el-tabs__item:hover) {
  color: var(--primary-color);
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary-color);
  font-weight: 600;
}

.custom-tabs :deep(.el-tabs__active-bar) {
  background: var(--primary-gradient);
  height: 3px;
  border-radius: 3px;
}

.profile-form {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 15px;
  box-shadow: var(--shadow-sm);
  transition: all 0.4s ease;
}

.profile-form:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  background: rgba(255, 255, 255, 0.8);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
  position: relative;
}

.avatar-container {
  margin-bottom: 15px;
  position: relative;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 600;
  position: relative;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 5px 15px rgba(94, 114, 235, 0.3);
  overflow: hidden;
}

.avatar-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transform: translateX(-100%);
  animation: avatarShine 3s infinite;
}

@keyframes avatarShine {
  0% { transform: translateX(-100%); }
  20%, 100% { transform: translateX(100%); }
}

.avatar:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 10px 25px rgba(94, 114, 235, 0.4);
}

.avatar-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: white;
  color: var(--primary-color);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 10px;
  border-radius: 15px;
  box-shadow: var(--shadow-sm);
  transform: translate(10%, 10%);
  border: 2px solid var(--primary-color);
  animation: badgePulse 2s infinite alternate;
}

@keyframes badgePulse {
  0% { box-shadow: 0 0 0 0 rgba(94, 114, 235, 0.4); }
  100% { box-shadow: 0 0 0 10px rgba(94, 114, 235, 0); }
}

.username-display {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 5px;
  text-align: center;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
}

.username-display::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background: var(--primary-gradient);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.username-display:hover::after {
  width: 80px;
}

/* 自定义输入框样式 */
.custom-input {
  transition: all 0.3s ease;
}

.custom-input:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
  border-radius: 10px !important;
  padding: 5px 15px;
  transition: all 0.3s ease;
}

.custom-input:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary-color) !important;
  transform: translateY(-2px);
}

.custom-input:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(94, 114, 235, 0.3) !important;
}

.form-icon {
  color: #5e72eb;
  font-size: 16px;
  margin-right: 8px;
  transition: all 0.3s ease;
}

.custom-input:deep(.el-input__wrapper.is-focus) .form-icon {
  transform: scale(1.2);
}

/* 提交按钮样式 */
.submit-btn {
  background: var(--primary-gradient) !important;
  border: none !important;
  padding: 12px 25px !important;
  border-radius: 10px !important;
  font-size: 16px !important;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
  box-shadow: 0 4px 15px rgba(94, 114, 235, 0.3) !important;
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(94, 114, 235, 0.4) !important;
  letter-spacing: 1px;
}

.btn-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transform: rotate(30deg);
  animation: btnShine 6s infinite;
  animation-play-state: paused;
}

.submit-btn:hover .btn-shine {
  animation-play-state: running;
}

@keyframes btnShine {
  0% {
    transform: translateX(-200%) rotate(30deg);
  }
  20%, 100% {
    transform: translateX(300%) rotate(30deg);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .user-profile {
    padding: 20px 15px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .profile-form {
    padding: 15px;
  }
  
  .avatar {
    width: 100px;
    height: 100px;
    font-size: 40px;
  }
  
  .custom-tabs :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 15px;
  }
  
  .submit-btn {
    width: 100%;
  }
}
</style> 