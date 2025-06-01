<template>
  <app-layout>
    <div class="data-statistics">
      <div class="page-header">
        <h2>数据统计</h2>
      </div>
      
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="statistic-card">
            <div class="statistic-content">

              <div class="statistic-data">
                <div class="statistic-value">{{ courseCount }}</div>
                <div class="statistic-label">课程数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="statistic-card">
            <div class="statistic-content">

              <div class="statistic-data">
                <div class="statistic-value">{{ studentCount }}</div>
                <div class="statistic-label">学生数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="statistic-card">
            <div class="statistic-content">

              <div class="statistic-data">
                <div class="statistic-value">{{ questionCount }}</div>
                <div class="statistic-label">问题数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="statistic-card">
            <div class="statistic-content">

              <div class="statistic-data">
                <div class="statistic-value">{{ answerCount }}</div>
                <div class="statistic-label">答案数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <span style="width: 100px;">学生答题情况</span>
                <el-select v-model="selectedCourse" placeholder="选择课程" clearable>
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
    
    courseCount.value = data.course_count || 0
    studentCount.value = data.student_count || 0
    questionCount.value = data.question_count || 0
    answerCount.value = data.answer_count || 0
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
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.score_range)
      },
      yAxis: {
        type: 'value',
        name: '学生数量'
      },
      series: [
        {
          name: '学生数量',
          type: 'bar',
          data: data.map(item => item.count),
          itemStyle: {
            color: function(params) {
              const colorList = ['#ff6b6b', '#feca57', '#1dd1a1', '#48dbfb', '#00d2d3']
              return colorList[params.dataIndex]
            }
          }
        }
      ]
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
.data-statistics {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.statistic-card {
  margin-bottom: 20px;
  height: 110px;
}

.statistic-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.statistic-icon {
  font-size: 36px;
  width: 60px;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  background-color: #ecf5ff;
  color: #409EFF;
  margin-right: 15px;
}

.statistic-data {
  flex: 1;
}

.statistic-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.statistic-label {
  color: #909399;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 400px;
}

.empty-chart {
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style> 