import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import App from './App.vue'

// 注意：不再需要导入全局语音识别工具
// 我们已经通过HTML页面中的script标签加载了它

// 导入路由组件
import Home from './views/Home.vue'
import Login from './views/Login.vue'
import CourseList from './views/student/CourseList.vue'
import CourseDetail from './views/student/CourseDetail.vue'
import ChatHistory from './views/student/ChatHistory.vue'
import LevelAnalysis from './views/student/LevelAnalysis.vue'
import SystemSettings from './views/SystemSettings.vue'
import CourseManagement from './views/teacher/CourseManagement.vue'
import StudentManagement from './views/teacher/StudentManagement.vue'
import DataStatistics from './views/teacher/DataStatistics.vue'
import TeacherCourseDetail from './views/teacher/CourseDetail.vue'
import AiAssistant from './views/student/AiAssistant.vue'
import UserProfile from './views/UserProfile.vue'
import Test  from './views/test.vue'

// 配置axios
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.withCredentials = true

// 添加请求拦截器
axios.interceptors.request.use(
  config => {
    console.log('API请求:', config.method.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 添加响应拦截器
axios.interceptors.response.use(
  response => {
    console.log('API响应成功:', response.config.url)
    return response
  },
  error => {
    console.error('API响应错误:', error.config?.url, error.message)
    if (error.response) {
      console.error('状态码:', error.response.status)
      
      // 如果是401未授权错误，跳转到登录页面
      if (error.response.status === 401) {
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/courses', component: CourseList },
    { path: '/courses/:id', component: CourseDetail },
    { path: '/chat-history', component: ChatHistory },
    { path: '/level-analysis', component: LevelAnalysis },
    { path: '/settings', component: SystemSettings },
    { path: '/profile', component: UserProfile },
    { path: '/course-management', component: CourseManagement },
    { path: '/course-detail/:id', component: TeacherCourseDetail },
    { path: '/student-management', component: StudentManagement },
    { path: '/data-statistics', component: DataStatistics },
    { path: '/ai-assistant/:id', component: AiAssistant },
    { path: '/test', component: Test }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  if (to.path !== '/login') {
    try {
      const response = await axios.get('/api/current_user')
      if (!response.data.logged_in) {
        next('/login')
      } else {
        next()
      }
    } catch (error) {
      next('/login')
    }
  } else {
    next()
  }
})

// 创建Pinia实例
const pinia = createPinia()

// 创建Vue应用
const app = createApp(App)
app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
