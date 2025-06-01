import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isLoggedIn: false
  }),
  
  getters: {
    isTeacher: (state) => {
      if (!state.currentUser || !state.currentUser.role) return false
      const role = state.currentUser.role.toLowerCase()
      return role === 'teacher' || role === '教师'
    },
    isStudent: (state) => {
      if (!state.currentUser || !state.currentUser.role) return false
      const role = state.currentUser.role.toLowerCase()
      return role === 'student' || role === '学生'
    },
    userId: (state) => state.currentUser?.id,
    username: (state) => state.currentUser?.username
  },
  
  actions: {
    async login(username, password) {
      try {
        console.log('执行登录请求...')
        const response = await axios.post('/api/login', { username, password })
        console.log('登录响应:', response.data)
        if (response.data.success) {
          this.currentUser = response.data.user
          this.isLoggedIn = true
          return { success: true }
        } else {
          return { success: false, message: response.data.message }
        }
      } catch (error) {
        console.error('登录失败:', error)
        return { success: false, message: error.response?.data?.message || '登录失败' }
      }
    },
    
    async logout() {
      try {
        await axios.post('/api/logout')
        this.currentUser = null
        this.isLoggedIn = false
        return { success: true }
      } catch (error) {
        console.error('登出失败:', error)
        return { success: false, message: '登出失败' }
      }
    },
    
    async checkAuth() {
      try {
        console.log('检查认证状态...')
        const response = await axios.get('/api/current_user')
        console.log('认证状态响应:', response.data)
        if (response.data.logged_in) {
          this.currentUser = response.data.user
          this.isLoggedIn = true
          return true
        } else {
          this.currentUser = null
          this.isLoggedIn = false
          return false
        }
      } catch (error) {
        console.error('认证检查失败:', error)
        this.currentUser = null
        this.isLoggedIn = false
        return false
      }
    }
  }
}) 