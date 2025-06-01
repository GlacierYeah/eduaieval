<template>
  <app-layout>
    <div class="data-statistics">
      <!-- 动态背景装饰 -->
      <div class="background-decoration"></div>
      
      <div class="page-header animate__animated animate__fadeInDown">
        <h2 class="title-gradient">数据统计</h2>
      </div>
      
      <el-row :gutter="20" class="animate__animated animate__fadeInUp" style="animation-delay: 0.1s">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="statistic-card-wrapper">
            <el-card class="statistic-card">
              <div class="statistic-content">
                <div class="statistic-icon courses-icon">
                  <i class="el-icon-reading"></i>
                </div>
                <div class="statistic-data">
                  <div class="statistic-value count-animation">{{ courseCount }}</div>
                  <div class="statistic-label">课程数量</div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <div class="statistic-card-wrapper" style="animation-delay: 0.2s">
            <el-card class="statistic-card">
              <div class="statistic-content">
                <div class="statistic-icon students-icon">
                  <i class="el-icon-user"></i>
                </div>
                <div class="statistic-data">
                  <div class="statistic-value count-animation">{{ studentCount }}</div>
                  <div class="statistic-label">学生数量</div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <div class="statistic-card-wrapper" style="animation-delay: 0.3s">
            <el-card class="statistic-card">
              <div class="statistic-content">
                <div class="statistic-icon questions-icon">
                  <i class="el-icon-question"></i>
                </div>
                <div class="statistic-data">
                  <div class="statistic-value count-animation">{{ questionCount }}</div>
                  <div class="statistic-label">问题数量</div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <div class="statistic-card-wrapper" style="animation-delay: 0.4s">
            <el-card class="statistic-card">
              <div class="statistic-content">
                <div class="statistic-icon answers-icon">
                  <i class="el-icon-chat-dot-round"></i>
                </div>
                <div class="statistic-data">
                  <div class="statistic-value count-animation">{{ answerCount }}</div>
                  <div class="statistic-label">答案数量</div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px" class="animate__animated animate__fadeInUp" style="animation-delay: 0.5s">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span class="chart-title">学生答题情况</span>
                <el-select v-model="selectedCourse" placeholder="选择课程" clearable class="course-select">
                  <el-option
                    v-for="course in courses"
                    :key="course.id"
                    :label="course.title"
                    :value="course.id"
                  ></el-option>
                </el-select>
              </div>
            </template>
            
            <div v-loading="loading">
              <div v-if="chartData.length === 0" class="empty-chart">
                <el-empty description="暂无数据"></el-empty>
              </div>
              <div v-else id="score-chart" class="chart-container"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'
import AppLayout from '../../components/AppLayout.vue'

// 统计数据
const courseCount = ref(0)
const studentCount = ref(0)
const questionCount = ref(0)
const answerCount = ref(0)
const loading = ref(false)

// 课程选择
const courses = ref([])
const selectedCourse = ref(null)
const chartData = ref([])
let chartInstance = null

// 获取统计数据
const fetchStatistics = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/statistics')
    const data = response.data
    
    // 使用setTimeout来创建数字增长效果
    setTimeout(() => {
      courseCount.value = data.course_count || 0
    }, 300)
    
    setTimeout(() => {
      studentCount.value = data.student_count || 0
    }, 500)
    
    setTimeout(() => {
      questionCount.value = data.question_count || 0
    }, 700)
    
    setTimeout(() => {
      answerCount.value = data.answer_count || 0
    }, 900)
  } catch (error) {
    console.error('获取统计数据失败', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 获取教师的课程列表
const fetchCourses = async () => {
  try {
    const response = await axios.get('/api/courses')
    courses.value = response.data.courses || []
  } catch (error) {
    console.error('获取课程列表失败', error)
    ElMessage.error('获取课程列表失败')
  }
}

// 获取学生答题情况
const fetchScoreData = async (courseId = null) => {
  loading.value = true
  
  try {
    const url = courseId 
      ? `/api/courses/${courseId}/score-statistics` 
      : '/api/score-statistics'
      
    const response = await axios.get(url)
    chartData.value = response.data.statistics || []
    
    if (chartData.value.length > 0) {
      renderChart()
    }
  } catch (error) {
    console.error('获取答题数据失败', error)
    ElMessage.error('获取答题数据失败')
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  // 由于后端API还未实现，使用模拟数据进行展示
  const mockData = [
    { score_range: '0-60', count: 5 },
    { score_range: '60-70', count: 12 },
    { score_range: '70-80', count: 18 },
    { score_range: '80-90', count: 25 },
    { score_range: '90-100', count: 8 }
  ]
  
  // 使用真实数据或模拟数据
  const data = chartData.value.length > 0 ? chartData.value : mockData
  
  setTimeout(() => {
    const chartDom = document.getElementById('score-chart')
    if (!chartDom) return
    
    chartInstance = echarts.init(chartDom)
    
    const option = {
      title: {
        text: '学生答题分数分布',
        left: 'center',
        textStyle: {
          color: '#334155',
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.score_range),
        axisLine: {
          lineStyle: {
            color: '#cbd5e1'
          }
        },
        axisTick: {
          alignWithLabel: true
        }
      },
      yAxis: {
        type: 'value',
        name: '学生数量',
        nameTextStyle: {
          color: '#64748b'
        },
        axisLine: {
          show: true,
          lineStyle: {
            color: '#cbd5e1'
          }
        },
        splitLine: {
          lineStyle: {
            color: '#f1f5f9'
          }
        }
      },
      series: [
        {
          name: '学生数量',
          type: 'bar',
          barWidth: '60%',
          data: data.map(item => ({
            value: item.count,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#5e72eb' },
                { offset: 1, color: '#00d2ff' }
              ])
            }
          })),
          showBackground: true,
          backgroundStyle: {
            color: 'rgba(180, 180, 180, 0.1)'
          },
          animationDelay: function (idx) {
            return idx * 100 + 200;
          }
        }
      ],
      animationEasing: 'elasticOut',
      animationDelayUpdate: function (idx) {
        return idx * 5;
      }
    }
    
    chartInstance.setOption(option)
    
    // 窗口大小变化时重绘图表
    window.addEventListener('resize', () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    })
  }, 100)
}

// 当选择的课程变化时重新获取数据
watch(() => selectedCourse.value, (newValue) => {
  fetchScoreData(newValue)
})

onMounted(() => {
  fetchStatistics()
  fetchCourses()
  fetchScoreData()
  
  // 模拟数据加载完毕后渲染图表
  setTimeout(() => {
    renderChart()
  }, 500)
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.data-statistics {
  padding: 20px;
  position: relative;
  min-height: calc(100vh - 100px);
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  overflow: hidden;
}

/* 动态背景效果 - 类似CourseList.vue */
.data-statistics::before {
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

/* 动态几何装饰 - 类似CourseList.vue */
.data-statistics::after {
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

/* 额外的背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.background-decoration::before {
  content: "";
  position: absolute;
  top: 10%;
  left: 5%;
  width: 200px;
  height: 200px;
  background: linear-gradient(45deg, rgba(94, 114, 235, 0.05), rgba(0, 210, 255, 0.05));
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  animation: morphShape 25s linear infinite alternate;
}

.background-decoration::after {
  content: "";
  position: absolute;
  bottom: 10%;
  right: 5%;
  width: 250px;
  height: 250px;
  background: linear-gradient(45deg, rgba(138, 43, 226, 0.05), rgba(94, 114, 235, 0.05));
  border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
  animation: morphShape 30s linear infinite alternate-reverse;
}

@keyframes morphShape {
  0% {
    border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  }
  25% {
    border-radius: 58% 42% 75% 25% / 76% 46% 54% 24%;
  }
  50% {
    border-radius: 50% 50% 33% 67% / 55% 27% 73% 45%;
  }
  75% {
    border-radius: 33% 67% 58% 42% / 63% 68% 32% 37%;
  }
  100% {
    border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
  }
}

.page-header {
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

.statistic-card-wrapper {
  margin-bottom: 20px;
  transform: translateY(50px);
  opacity: 0;
  animation: slideUp 0.5s forwards;
}

@keyframes slideUp {
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.statistic-card {
  height: 110px;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: none;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  position: relative;
}

.statistic-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(94, 114, 235, 0.05), rgba(0, 210, 255, 0.05));
  z-index: 0;
}

.statistic-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(94, 114, 235, 0.15);
}

.statistic-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.statistic-icon {
  font-size: 36px;
  width: 60px;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 12px;
  color: white;
  margin-right: 15px;
  transition: all 0.3s ease;
}

.courses-icon {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  box-shadow: 0 5px 15px rgba(94, 114, 235, 0.2);
}

.students-icon {
  background: linear-gradient(45deg, #8b5cf6, #ec4899);
  box-shadow: 0 5px 15px rgba(139, 92, 246, 0.2);
}

.questions-icon {
  background: linear-gradient(45deg, #10b981, #059669);
  box-shadow: 0 5px 15px rgba(16, 185, 129, 0.2);
}

.answers-icon {
  background: linear-gradient(45deg, #f59e0b, #d97706);
  box-shadow: 0 5px 15px rgba(245, 158, 11, 0.2);
}

.statistic-card:hover .statistic-icon {
  transform: scale(1.1) rotate(-10deg);
}

.statistic-data {
  flex: 1;
}

.statistic-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
  background: linear-gradient(45deg, #334155, #0f172a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.count-animation {
  display: inline-block;
  animation: countPulse 2s ease-in-out infinite alternate;
}

@keyframes countPulse {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.05);
  }
}

.statistic-label {
  color: #64748b;
  font-size: 14px;
  transition: all 0.3s ease;
}

.statistic-card:hover .statistic-label {
  color: #334155;
}

.chart-card {
  margin-bottom: 20px;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: none;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1;
  transform: translateY(30px);
  opacity: 0;
  animation: slideUp 0.5s forwards;
  animation-delay: 0.4s;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(94, 114, 235, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(45deg, rgba(94, 114, 235, 0.05), rgba(0, 210, 255, 0.05));
  padding: 15px 20px !important;
  border-bottom: 1px solid rgba(230, 230, 230, 0.5);
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
  position: relative;
}

.chart-title::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 30px;
  height: 2px;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.card-header:hover .chart-title::after {
  width: 50px;
}

.course-select {
  width: 200px;
  transition: all 0.3s ease;
}

.course-select:hover {
  transform: translateY(-2px);
}

.chart-container {
  height: 400px;
  padding: 10px;
  transition: all 0.3s ease;
}

.empty-chart {
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(45deg, rgba(94, 114, 235, 0.02), rgba(0, 210, 255, 0.02));
  border-radius: 12px;
  margin: 10px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .course-select {
    width: 100%;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style> 