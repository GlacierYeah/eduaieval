<template>
  <app-layout>
    <div class="course-list">
      <div class="page-header animate__animated animate__fadeInDown">
        <h2 class="title-gradient">课程列表</h2>
        <div class="search-container">
          <el-input
            v-model="searchText"
            placeholder="搜索课程"
            class="search-input"
            clearable
            prefix-icon="el-icon-search"
          >
            <template #prefix>
              <div class="search-icon-animate">
                <i class="el-icon-search"></i>
              </div>
            </template>
          </el-input>
        </div>
      </div>
      
      <div v-loading="loading">
        <transition-group
          name="course-list-transition"
          tag="div"
          appear
        >
          <el-empty 
            v-if="filteredCourses.length === 0" 
            description="暂无课程"
            class="animate__animated animate__fadeIn"
          ></el-empty>
          
          <el-row :gutter="20">
            <el-col 
              v-for="(course, index) in filteredCourses" 
              :key="course.id" 
              :xs="24" 
              :sm="12" 
              :md="8" 
              :lg="6"
              class="animate__animated animate__fadeInUp"
              :style="{ animationDelay: `${index * 0.1}s` }"
            >
              <div class="card-wrapper">
                <el-card 
                  class="course-card" 
                  shadow="hover" 
                  @click="viewCourse(course)"
                >
                  <div class="card-overlay"></div>
                  <div class="course-image">
                    <img v-if="course.image_path" :src="getImageUrl(course.image_path)" alt="课程图片" />
                    <div v-else class="no-image">
                      <el-icon><el-icon-picture /></el-icon>
                    </div>
                    <div class="course-badge">热门</div>
                  </div>
                  <div class="course-info">
                    <h3>{{ course.title }}</h3>
                    <p class="description">{{ course.description }}</p>
                  </div>
                  <div class="course-footer">
                    <el-button 
                      type="primary" 
                      size="small" 
                      class="view-button"
                      @click.stop="viewCourse(course)"
                    >
                      查看课程
                      <i class="el-icon-right"></i>
                    </el-button>
                  </div>
                </el-card>
              </div>
            </el-col>
          </el-row>
        </transition-group>
      </div>

      <!-- 自定义加载动画 -->
      <div v-if="loading" class="custom-loader">
        <div class="loader-circle"></div>
        <div class="loader-text">加载课程中...</div>
      </div>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'

const router = useRouter()
const courses = ref([])
const loading = ref(false)
const searchText = ref('')

// 根据搜索文本过滤课程
const filteredCourses = computed(() => {
  if (!searchText.value) return courses.value
  
  const searchLower = searchText.value.toLowerCase()
  return courses.value.filter(course => 
    course.title.toLowerCase().includes(searchLower) || 
    course.description.toLowerCase().includes(searchLower)
  )
})

// 获取课程列表
const fetchCourses = async () => {
  loading.value = true
  try {
    console.log('开始获取课程列表...')
    // 使用正确的API路径，添加/api前缀
    const response = await axios.get('/api/courses')
    console.log('课程列表响应:', response)
    
    if (response.data.success) {
      courses.value = response.data.courses || []
      console.log(`成功获取到 ${courses.value.length} 个课程`)
      if (courses.value.length === 0) {
        ElMessage.info('暂无课程数据')
      }
    } else {
      console.error('获取课程列表失败:', response.data.message)
      ElMessage.error(response.data.message || '获取课程列表失败')
    }
  } catch (error) {
    console.error('获取课程列表发生错误:', error)
    if (error.response) {
      console.error('错误响应数据:', error.response.data)
      console.error('错误状态码:', error.response.status)
    }
    ElMessage.error('获取课程列表失败，请检查网络连接或登录状态')
  } finally {
    setTimeout(() => {
      loading.value = false
    }, 600) // 延迟关闭加载状态，使动画效果更明显
  }
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  return `http://localhost:5000/static/uploads/${path}`
}

// 查看课程详情
const viewCourse = (course) => {
  router.push(`/courses/${course.id}`)
}

// 组件挂载时获取课程列表
onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.course-list {
  padding: 20px;
  position: relative;
  min-height: calc(100vh - 100px);
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  overflow: hidden;
}

/* 动态背景效果 */
.course-list::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 10% 10%, rgba(94, 114, 235, 0.08), transparent 30%),
    radial-gradient(circle at 90% 30%, rgba(0, 210, 255, 0.07), transparent 40%),
    radial-gradient(circle at 20% 80%, rgba(138, 43, 226, 0.05), transparent 35%);
  z-index: 0;
  pointer-events: none;
  animation: backgroundPulse 15s infinite alternate ease-in-out;
}

@keyframes backgroundPulse {
  0% { opacity: 0.6; }
  50% { opacity: 0.8; }
  100% { opacity: 0.6; }
}

/* 添加动态几何装饰 */
.course-list::after {
  content: '';
  position: absolute;
  bottom: -50px;
  right: -50px;
  width: 300px;
  height: 300px;
  border-radius: 35% 65% 65% 35% / 35% 45% 55% 65%;
  background: linear-gradient(135deg, rgba(94, 114, 235, 0.08) 0%, rgba(0, 210, 255, 0.08) 100%);
  z-index: 0;
  pointer-events: none;
  animation: shapeFloat 20s infinite alternate ease-in-out;
}

@keyframes shapeFloat {
  0% { transform: rotate(0deg) translate(0, 0); }
  50% { transform: rotate(15deg) translate(-20px, -20px); }
  100% { transform: rotate(0deg) translate(0, 0); }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px 25px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1;
  transition: all 0.4s ease;
}

.page-header:hover {
  box-shadow: 0 8px 25px rgba(94, 114, 235, 0.12);
  transform: translateY(-2px);
}

.title-gradient {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
  letter-spacing: 0.5px;
}

.title-gradient::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 50px;
  height: 3px;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.page-header:hover .title-gradient::after {
  width: 80px;
}

.search-container {
  position: relative;
  width: 300px;
  z-index: 2;
}

.search-input {
  width: 100%;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.search-input:deep(.el-input__inner) {
  width: 100%;
  height:44px;
  font-size:15px;
  background: rgba(255,255,255,0.8);
  transition: all 0.4s cubic-bezier(0.165,0.84,0.44,1);
  transform: translateY(-3px);
  transform: translateX(-40px);
}

.search-icon-animate {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  color: #5e72eb;
}

.search-input:deep(.el-input__inner:focus) + .search-icon-animate {
  transform: scale(1.2);
  color: #5e72eb;
}

.card-wrapper {
  perspective: 1000px;
  margin-bottom: 20px;
  height: 100%;
  transition: all 0.3s ease;
}

.course-card {
  margin-bottom: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.6s cubic-bezier(0.165, 0.84, 0.44, 1);
  position: relative;
  overflow: hidden;
  transform-style: preserve-3d;
  border-radius: 16px !important;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8) !important;
  box-shadow: 0 10px 20px rgba(94, 114, 235, 0.08) !important;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(94, 114, 235, 0.1) 0%, rgba(0, 210, 255, 0.1) 100%);
  opacity: 0;
  transition: all 0.4s ease;
  z-index: 1;
  pointer-events: none;
}

.course-card:hover {
  transform: translateY(-15px) rotateX(5deg) rotateY(2deg);
  box-shadow: 0 25px 40px rgba(94, 114, 235, 0.18) !important;
}

.course-card:hover .card-overlay {
  opacity: 1;
}

.course-image {
  height: 180px;
  overflow: hidden;
  margin-bottom: 15px;
  position: relative;
  border-radius: 12px;
  transition: all 0.5s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.course-image::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 40%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.4), transparent);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.course-card:hover .course-image::after {
  opacity: 1;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 1s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.course-card:hover .course-image img {
  transform: scale(1.08);
}

.course-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background: linear-gradient(45deg, #5e72eb, #FF6B8B);
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 5px 15px rgba(94, 114, 235, 0.3);
  opacity: 0;
  transform: translateX(20px);
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 2;
}

.course-card:hover .course-badge {
  opacity: 1;
  transform: translateX(0);
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
  color: #5e72eb;
  font-size: 40px;
  border-radius: 12px;
  transition: all 0.4s ease;
}

.course-card:hover .no-image {
  transform: scale(1.05);
  box-shadow: 0 10px 25px rgba(94, 114, 235, 0.2);
}

.course-info {
  flex: 1;
  padding: 0 20px;
  position: relative;
  z-index: 2;
}

.course-info h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #303133;
  transition: all 0.4s ease;
  font-weight: 600;
  position: relative;
  padding-left: 15px;
}

.course-info h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: linear-gradient(to bottom, #5e72eb, #00d2ff);
  border-radius: 3px;
  transition: height 0.3s ease;
}

.course-card:hover .course-info h3 {
  color: #5e72eb;
  transform: translateX(5px);
}

.course-card:hover .course-info h3::before {
  height: 25px;
}

.description {
  color: #606266;
  font-size: 14px;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.6;
  transition: all 0.3s ease;
}

.course-card:hover .description {
  color: #303133;
}

.course-footer {
  margin-top: 20px;
  padding: 0 20px 20px;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 2;
}

.view-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(45deg, #5e72eb, #00d2ff) !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 12px 0 !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  box-shadow: 0 5px 15px rgba(94, 114, 235, 0.2);
}

.view-button:hover {
  letter-spacing: 1px;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(94, 114, 235, 0.3);
}

.view-button i {
  margin-left: 5px;
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.view-button:hover i {
  transform: translateX(5px);
}

/* 添加闪光效果 */
.view-button::before {
  content: '';
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
  animation: shine 6s infinite;
  animation-play-state: paused;
}

.view-button:hover::before {
  animation-play-state: running;
}

@keyframes shine {
  0% {
    transform: translateX(-200%) rotate(30deg);
  }
  20%, 100% {
    transform: translateX(300%) rotate(30deg);
  }
}

/* 列表过渡动画 */
.course-list-transition-enter-active,
.course-list-transition-leave-active {
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.course-list-transition-enter-from,
.course-list-transition-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.course-list-transition-move {
  transition: transform 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
}

/* 自定义加载动画 */
.custom-loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loader-circle {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
  animation: rotate-layers 3s linear infinite;
}

.loader-circle::before, 
.loader-circle::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  animation: pulse-shadow 2s ease-in-out infinite alternate;
}

.loader-circle::before {
  background: linear-gradient(135deg, #5e72eb 0%, transparent 50%);
  box-shadow: 0 0 20px rgba(94, 114, 235, 0.5);
}

.loader-circle::after {
  background: linear-gradient(315deg, #00d2ff 0%, transparent 50%);
  box-shadow: 0 0 20px rgba(0, 210, 255, 0.5);
  animation-delay: -1s;
}

@keyframes rotate-layers {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse-shadow {
  0% { 
    transform: scale(0.8);
    opacity: 0.5;
  }
  100% { 
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.loader-text {
  margin-top: 30px;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
  animation: text-pulse 1.5s infinite alternate ease-in-out;
  text-shadow: 0 2px 10px rgba(94, 114, 235, 0.2);
}

@keyframes text-pulse {
  0% { 
    opacity: 0.7; 
    transform: scale(1);
    letter-spacing: 1px;
  }
  100% { 
    opacity: 1; 
    transform: scale(1.05);
    letter-spacing: 2px;
  }
}

/* 给空状态添加动画 */
.el-empty {
  position: relative;
  z-index: 2;
  animation: fadeIn 1s cubic-bezier(0.165, 0.84, 0.44, 1);
  transition: all 0.3s ease;
}

.el-empty:hover {
  transform: scale(1.05);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .search-container {
    width: 100%;
  }

  .course-card:hover {
    transform: translateY(-10px);
  }
}

/* 添加一些额外的光影效果 */
.card-wrapper:nth-child(3n+1) .course-card::before {
  content: '';
  position: absolute;
  top: -30px;
  right: -30px;
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, rgba(94, 114, 235, 0.2), rgba(0, 210, 255, 0.2));
  border-radius: 50%;
  filter: blur(30px);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
  z-index: 0;
}

.card-wrapper:nth-child(3n+2) .course-card::before {
  content: '';
  position: absolute;
  bottom: -30px;
  left: -30px;
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, rgba(0, 210, 255, 0.2), rgba(138, 43, 226, 0.2));
  border-radius: 50%;
  filter: blur(30px);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
  z-index: 0;
}

.card-wrapper:nth-child(3n) .course-card::before {
  content: '';
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(94, 114, 235, 0.2));
  border-radius: 50%;
  filter: blur(30px);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
  z-index: 0;
}

.card-wrapper:hover .course-card::before {
  opacity: 1;
}
</style> 