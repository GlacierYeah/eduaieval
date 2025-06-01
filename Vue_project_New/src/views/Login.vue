<template>
  <div class="login-container">
    <div class="wave-container">
      <div class="wave wave1"></div>
      <div class="wave wave2"></div>
      <div class="wave wave3"></div>
    </div>
    
    <div class="login-box animate__animated animate__fadeInUp">
      <h2 class="title-glow">学习效果智能评估系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="username" class="animate__animated animate__fadeInLeft animate__delay-1s">
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名" 
            prefix-icon="el-icon-user"
            class="custom-input"
          ></el-input>
        </el-form-item>
        <el-form-item prop="password" class="animate__animated animate__fadeInRight animate__delay-1s">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="el-icon-lock"
            class="custom-input"
          ></el-input>
        </el-form-item>
        <el-form-item class="animate__animated animate__fadeIn animate__delay-1s">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-radio-group v-model="loginForm.role" class="role-selector">
                <el-radio label="teacher">教师</el-radio>
                <el-radio label="student">学生</el-radio>
              </el-radio-group>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="text" class="forget-btn">忘记密码?</el-button>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item class="animate__animated animate__fadeInUp animate__delay-2s">
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-button pulse-hover" 
            @click="submitLogin"
          >
            <span class="btn-text">登录</span>
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="demo-accounts animate__animated animate__fadeIn animate__delay-2s">
        <p>示例账号:</p>
        <p>教师: teacher1 / 123456</p>
        <p>学生: student1 / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  role: 'student'
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度需在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度需在6-20个字符之间', trigger: 'blur' }
  ]
}

// 登录提交
const submitLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    
    loading.value = true
    const result = await userStore.login(loginForm.username, loginForm.password)
    
    if (result.success) {
      ElMessage.success('登录成功')
      
      // 根据用户角色跳转到不同页面
      if (userStore.isTeacher) {
        router.push('/course-management')
      } else {
        router.push('/courses')
      }
    } else {
      ElMessage.error(result.message || '登录失败')
    }
  } catch (error) {
    console.error('登录验证失败', error)
  } finally {
    loading.value = false
  }
}

// 页面加载动画
onMounted(() => {
  document.documentElement.style.setProperty('--animate-duration', '0.8s');
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
  position: relative;
  overflow: hidden;
}

.wave-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100px;
  overflow: hidden;
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200%;
  height: 100px;
  background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 0v46.29c47.79 22.2 103.59 32.17 158 28 70.36-5.37 136.33-33.31 206.8-37.5 73.84-4.36 147.54 16.88 218.2 35.26 69.27 18 138.3 24.88 209.4 13.08 36.15-6 69.85-17.84 104.45-29.34C989.49 25 1113-14.29 1200 52.47V0z" opacity=".25" fill="white"/></svg>');
  background-size: 1200px 100px;
  animation: wave 25s linear infinite;
}

.wave1 {
  animation: wave 25s linear infinite;
  z-index: 3;
  opacity: 0.5;
}

.wave2 {
  animation: wave-reverse 20s linear infinite;
  bottom: 10px;
  opacity: 0.3;
  z-index: 2;
}

.wave3 {
  animation: wave 30s linear infinite;
  bottom: 15px;
  opacity: 0.2;
  z-index: 1;
}

@keyframes wave {
  0% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(-50%);
  }
  100% {
    transform: translateX(0);
  }
}

@keyframes wave-reverse {
  0% {
    transform: translateX(-50%);
  }
  50% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.login-box {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
}

.login-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.title-glow {
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
}

.title-glow::after {
  content: '智能教育系统';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  z-index: -1;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: blur(5px);
  opacity: 0.7;
}

.login-form {
  margin-bottom: 20px;
}
.custom-input{
  width: 100%;
  height: 46px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}


.role-selector :deep(.el-radio__input.is-checked .el-radio__inner) {
  background-color: #3a7bd5;
  border-color: #3a7bd5;
}

.role-selector :deep(.el-radio__label) {
  transition: all 0.3s ease;
}

.role-selector :deep(.el-radio__input.is-checked+.el-radio__label) {
  color: #3a7bd5;
  font-weight: 500;
}

.login-button {
  width: 100%;
  height: 46px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
  border: none !important;
  transition: all 0.4s ease;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.6s ease;
}

.login-button:hover::before {
  left: 100%;
}

.pulse-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(58, 123, 213, 0.3);
}

.btn-text {
  position: relative;
  z-index: 1;
}

.forget-btn {
  color: #3a7bd5;
  transition: all 0.3s ease;
}

.forget-btn:hover {
  color: #00d2ff;
  text-decoration: underline;
}

.demo-accounts {
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px dashed #d9d9d9;
  font-size: 13px;
  color: #909399;
  text-align: center;
}

.demo-accounts p {
  margin: 5px 0;
  transition: all 0.3s ease;
}

.demo-accounts p:hover {
  color: #606266;
  transform: translateX(5px);
}

@keyframes floatAnimation {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0);
  }
}
</style> 