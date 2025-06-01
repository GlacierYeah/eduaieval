<template>
  <app-layout>
    <div class="level-analysis">
      <div class="page-header animate__animated animate__fadeInDown">
        <h2 class="title-gradient">等级分析</h2>
      </div>
      
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="analysis-card animate__animated animate__fadeInUp">
            <template #header>
              <div class="card-header">
                <span class="card-title">学习进度概览</span>
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="refreshData"
                  class="refresh-btn"
                >
                  <i class="refresh-icon"></i>刷新数据
                </el-button>
              </div>
            </template>
            
            <div v-if="loading" class="loading-container">
              <div class="chart-loader">
                <div class="circle-pulse"></div>
                <div class="circle-pulse"></div>
                <div class="circle-pulse"></div>
              </div>
              <p class="loading-text">正在分析您的学习数据...</p>
            </div>
            
            <div v-else-if="hasData" class="charts-container">
              <el-row :gutter="20">
                <el-col :xs="24" :md="12">
                  <div class="chart-wrapper animate__animated animate__fadeIn animate__delay-1s">
                    <h3 class="chart-title">
                      <i class="chart-icon pie-icon"></i>
                      课程完成进度
                    </h3>
                    <div ref="courseProgressChartRef" class="chart"></div>
                  </div>
                </el-col>
                <el-col :xs="24" :md="12">
                  <div class="chart-wrapper animate__animated animate__fadeIn animate__delay-1s">
                    <h3 class="chart-title">
                      <i class="chart-icon bar-icon"></i>
                      最近题目得分
                    </h3>
                    <div ref="recentScoresChartRef" class="chart"></div>
                  </div>
                </el-col>
              </el-row>
              
              <el-row :gutter="20" class="mt-20">
                <el-col :span="24">
                  <div class="chart-wrapper animate__animated animate__fadeIn animate__delay-2s">
                    <h3 class="chart-title">
                      <i class="chart-icon trend-icon"></i>
                      近期学习趋势
                    </h3>
                    <div ref="trendChartRef" class="chart"></div>
                  </div>
                </el-col>
              </el-row>
              
              <el-row :gutter="20" class="mt-20">
                <el-col :span="24">
                  <div class="data-summary animate__animated animate__fadeIn animate__delay-2s">
                    <h3 class="summary-title">学习数据摘要</h3>
                    <el-descriptions :column="3" border class="custom-descriptions">
                      <el-descriptions-item label="累计学习时长" class="stat-item">
                        <div class="stat-content">
                          <span class="stat-value">{{ statistics.totalLearningHours || 0 }}</span>
                          <span class="stat-unit">小时</span>
                        </div>
                      </el-descriptions-item>
                      <el-descriptions-item label="已完成课程" class="stat-item">
                        <div class="stat-content">
                          <span class="stat-value">{{ statistics.completedCourses || 0 }}</span>
                          <span class="stat-unit">个</span>
                        </div>
                      </el-descriptions-item>
                      <el-descriptions-item label="总答题数" class="stat-item">
                        <div class="stat-content">
                          <span class="stat-value">{{ statistics.totalQuestions || 0 }}</span>
                          <span class="stat-unit">题</span>
                        </div>
                      </el-descriptions-item>
                      <el-descriptions-item label="平均分数" class="stat-item">
                        <div class="stat-content">
                          <span class="stat-value score-value">{{ formatScore(statistics.averageScore) }}</span>
                        </div>
                      </el-descriptions-item>
                      <el-descriptions-item label="最高分课程" class="stat-item">
                        <div class="stat-content course-name">
                          {{ statistics.highestCourse || '暂无' }}
                        </div>
                      </el-descriptions-item>
                      <el-descriptions-item label="学习效率评级" class="stat-item">
                        <el-tag 
                          :type="getEfficiencyTagType()" 
                          class="efficiency-tag"
                        >
                          {{ statistics.efficiencyRating || '良好' }}
                        </el-tag>
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div v-else class="empty-content">
              <el-empty description="暂无学习数据"></el-empty>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const hasData = ref(false)

// 图表DOM引用
const courseProgressChartRef = ref(null)
const recentScoresChartRef = ref(null)
const trendChartRef = ref(null)

// 图表实例
let courseProgressChart = null
let recentScoresChart = null
let trendChart = null

// 统计数据
const statistics = reactive({
  totalLearningHours: 0,
  completedCourses: 0,
  totalQuestions: 0,
  averageScore: 0,
  highestCourse: '',
  efficiencyRating: '良好',
  courseProgress: [],
  categoryScores: [],
  recentQuestionScores: [],
  weeklyActivity: [],
  monthlyProgress: [],
  learningTrend: {
    dates: [],
    hours: [],
    questions: []
  }
})

// 格式化分数
const formatScore = (score) => {
  return score ? score.toFixed(1) : '0.0'
}

// 获取效率评级标签类型
const getEfficiencyTagType = () => {
  const rating = statistics.efficiencyRating
  if (rating === '优秀') return 'success'
  if (rating === '良好') return 'warning'
  if (rating === '一般') return 'info'
  return 'danger'
}

// 初始化课程进度图表（饼图）
const initCourseProgressChart = () => {
  if (!courseProgressChartRef.value) return
  
  if (courseProgressChart) {
    courseProgressChart.dispose()
  }
  
  courseProgressChart = echarts.init(courseProgressChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: statistics.courseProgress.map(item => item.name)
    },
    series: [
      {
        name: '课程进度',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: statistics.courseProgress
      }
    ]
  }
  
  courseProgressChart.setOption(option)
}

// 初始化最近题目得分图表（柱状图）
const initRecentScoresChart = () => {
  if (!recentScoresChartRef.value) {
    console.error('直方图DOM引用不存在')
    return
  }
  
  if (recentScoresChart) {
    recentScoresChart.dispose()
  }
  
  console.log('正在初始化直方图，数据：', statistics.recentQuestionScores)
  
  // 确保有数据可以显示
  if (!statistics.recentQuestionScores || statistics.recentQuestionScores.length === 0) {
    console.warn('没有题目得分数据，无法初始化直方图')
    return
  }
  
  recentScoresChart = echarts.init(recentScoresChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const data = params[0];
        return `${data.name}<br/>${data.value}分<br/>${statistics.recentQuestionScores[data.dataIndex]?.courseName || ''}`;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: statistics.recentQuestionScores.map(item => item.questionTitle || `题目${item.questionId}`),
      axisLabel: {
        interval: 0,
        rotate: 45,
        textStyle: {
          fontSize: 10
        },
        formatter: function (value) {
          return value.length > 10 ? value.substring(0, 10) + '...' : value;
        }
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      name: '分数'
    },
    series: [
      {
        name: '得分',
        type: 'bar',
        barWidth: '60%',
        data: statistics.recentQuestionScores.map(item => ({
          value: item.score,
          itemStyle: { 
            color: getScoreColor(item.score)
          }
        })),
        label: {
          show: true,
          position: 'top',
          formatter: '{c} 分'
        }
      }
    ]
  }
  
  try {
    recentScoresChart.setOption(option)
    console.log('直方图初始化成功')
  } catch (e) {
    console.error('直方图设置选项失败:', e)
  }
}

// 根据分数获取颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#67C23A';
  if (score >= 75) return '#409EFF';
  if (score >= 60) return '#E6A23C';
  return '#F56C6C';
}

// 初始化学习趋势图表（折线图）
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(trendChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['学习时长(小时)', '完成题目数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: statistics.learningTrend.dates
    },
    yAxis: [
      {
        type: 'value',
        name: '学习时长(小时)',
        position: 'left'
      },
      {
        type: 'value',
        name: '完成题目数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '学习时长(小时)',
        type: 'line',
        data: statistics.learningTrend.hours,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '完成题目数',
        type: 'line',
        yAxisIndex: 1,
        data: statistics.learningTrend.questions,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#67C23A'
        },
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  if (courseProgressChart) courseProgressChart.resize()
  if (recentScoresChart) recentScoresChart.resize()
  if (trendChart) trendChart.resize()
}

// 获取学习统计数据
const fetchStatisticsData = async () => {
  loading.value = true
  hasData.value = false
  
  try {
    // 获取用户学习统计数据
    const response = await axios.get('/api/student/learning-analytics')
    
    if (response.data.success) {
      const data = response.data
      
      // 基本统计数据
      statistics.totalLearningHours = data.total_learning_hours || 0
      statistics.completedCourses = data.completed_courses || 0
      statistics.totalQuestions = data.total_questions || 0
      statistics.averageScore = data.average_score || 0
      statistics.highestCourse = data.highest_course || '暂无'
      statistics.efficiencyRating = data.efficiency_rating || '良好'
      
      // 处理课程进度数据
      if (data.course_progress && data.course_progress.length > 0) {
        statistics.courseProgress = data.course_progress
      } else {
        // 生成模拟数据
        statistics.courseProgress = [
          { value: 30, name: '已完成' },
          { value: 40, name: '进行中' },
          { value: 30, name: '未开始' }
        ]
      }
      
      // 处理最近题目得分数据
      if (data.recent_question_scores && data.recent_question_scores.length > 0) {
        // 确保数据格式正确
        statistics.recentQuestionScores = data.recent_question_scores.map(item => {
          return {
            questionId: item.questionId || item.question_id || 0,
            questionTitle: item.questionTitle || item.question_title || `题目${item.questionId || item.question_id || 0}`,
            score: item.score || 0,
            courseName: item.courseName || item.course_name || '未知课程'
          }
        })
        console.log('处理后的题目得分数据:', statistics.recentQuestionScores)
      } else {
        console.warn('API返回的得分数据为空，使用模拟数据')
        // 使用模拟数据
        statistics.recentQuestionScores = [
          { questionId: 1, questionTitle: "英语听力理解题1", score: 85, courseName: "英语基础" },
          { questionId: 2, questionTitle: "英语口语练习2", score: 70, courseName: "英语基础" },
          { questionId: 3, questionTitle: "阅读理解与分析3", score: 90, courseName: "阅读理解" },
          { questionId: 4, questionTitle: "写作基础练习4", score: 60, courseName: "写作基础" }
        ]
      }
      
      // 学习趋势数据
      if (data.learning_trend && data.learning_trend.dates && data.learning_trend.dates.length > 0) {
        statistics.learningTrend.dates = data.learning_trend.dates || []
        statistics.learningTrend.hours = data.learning_trend.hours || []
        statistics.learningTrend.questions = data.learning_trend.questions || []
      } else {
        // 如果没有趋势数据，生成最近7天的空数据
        const dates = []
        const now = new Date()
        for (let i = 6; i >= 0; i--) {
          const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
          dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
        }
        statistics.learningTrend.dates = dates
        statistics.learningTrend.hours = Array(7).fill(0)
        statistics.learningTrend.questions = Array(7).fill(0)
      }
      
      hasData.value = true
      console.log('获取到数据，准备初始化图表')
      
      // 在获取到数据后立即尝试初始化图表
      initChartsNow()
      
      // 再使用nextTick确保DOM已经渲染完成
      nextTick(() => {
        console.log('DOM更新完成，再次尝试初始化图表')
        initChartsWithDelay() // 使用延迟函数替代直接调用
      })
    } else {
      console.error('获取学习统计数据失败：', response.data.message)
      ElMessage.error(response.data.message || '获取学习统计数据失败')
    }
  } catch (error) {
    console.error('获取学习统计数据失败', error)
    ElMessage.error('获取学习统计数据失败，请稍后重试')
    
    // 如果API暂未实现，使用模拟数据（生产环境可移除此段）
    console.log('使用模拟数据进行测试...')
    mockStatisticsData()
  } finally {
    loading.value = false
  }
}

// 尝试立即初始化图表
const initChartsNow = () => {
  console.log('立即尝试初始化图表')
  try {
    if (hasData.value) {
      if (courseProgressChartRef.value && !courseProgressChart) {
        initCourseProgressChart()
      }
      
      if (recentScoresChartRef.value && !recentScoresChart && 
          statistics.recentQuestionScores && statistics.recentQuestionScores.length > 0) {
        console.log('立即初始化直方图')
        initRecentScoresChart()
      }
      
      if (trendChartRef.value && !trendChart) {
        initTrendChart()
      }
    }
  } catch (e) {
    console.error('立即初始化图表失败:', e)
  }
}

// 仅用于开发测试：模拟数据（生产环境可移除）
const mockStatisticsData = () => {
  // 基本统计数据
  statistics.totalLearningHours = 45.5
  statistics.completedCourses = 3
  statistics.totalQuestions = 258
  statistics.averageScore = 82.5
  statistics.highestCourse = '英语口语基础'
  statistics.efficiencyRating = '良好'
  
  // 课程进度数据
  statistics.courseProgress = [
    { value: 35, name: '已完成课程' },
    { value: 45, name: '进行中课程' },
    { value: 20, name: '未开始课程' }
  ]
  
  // 最近题目得分数据
  statistics.recentQuestionScores = [
    { questionId: 1, questionTitle: "英语听力理解题1", score: 85, courseName: "英语基础" },
    { questionId: 2, questionTitle: "英语口语练习2", score: 70, courseName: "英语基础" },
    { questionId: 3, questionTitle: "阅读理解与分析3", score: 90, courseName: "阅读理解" },
    { questionId: 4, questionTitle: "写作基础练习4", score: 60, courseName: "写作基础" },
    { questionId: 5, questionTitle: "词汇量测试5", score: 75, courseName: "英语基础" },
    { questionId: 6, questionTitle: "语法结构分析6", score: 95, courseName: "语法学习" },
    { questionId: 7, questionTitle: "口语表达练习7", score: 80, courseName: "口语训练" },
    { questionId: 8, questionTitle: "写作进阶训练8", score: 65, courseName: "写作进阶" }
  ]
  
  // 学习趋势数据
  const dates = []
  const now = new Date()
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
    dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
  }
  
  statistics.learningTrend = {
    dates: dates,
    hours: [2.5, 1.5, 3.0, 2.0, 1.8, 2.2, 3.5],
    questions: [15, 10, 25, 16, 12, 18, 30]
  }
  
  hasData.value = true
  console.log('使用模拟数据，准备初始化图表')
  
  // 确保数据和DOM都准备好
  nextTick(() => {
    console.log('DOM更新完成，开始初始化图表')
    setTimeout(() => {
      initChartsWithDelay() // 使用延迟函数替代直接调用
    }, 100) // 增加一点延迟
  })
}

// 刷新数据
const refreshData = () => {
  console.log('用户手动刷新数据')
  fetchStatisticsData()
}

// 组件挂载时初始化
onMounted(() => {
  console.log('组件挂载，开始获取数据')
  fetchStatisticsData()
  window.addEventListener('resize', handleResize)
  
  // 额外添加一个延迟初始化，确保在任何情况下都能尝试初始化图表
  setTimeout(() => {
    if (hasData.value && !courseProgressChart && !recentScoresChart && !trendChart) {
      console.log('延迟初始化图表')
      initChartsWithDelay()
    }
  }, 3000) // 延迟增加到3秒
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (courseProgressChart) courseProgressChart.dispose()
  if (recentScoresChart) recentScoresChart.dispose()
  if (trendChart) trendChart.dispose()
})

// 可能是等待时间不够长，增加延迟处理
const initChartsWithDelay = () => {
  console.log('开始初始化图表...')
  console.log('课程进度图DOM元素:', courseProgressChartRef.value)
  console.log('最近题目得分图DOM元素:', recentScoresChartRef.value)
  console.log('趋势图DOM元素:', trendChartRef.value)
  console.log('最近题目得分数据:', statistics.recentQuestionScores)
  
  // 使用setTimeout增加延迟确保DOM完全渲染和可见
  setTimeout(() => {
    try {
      if (hasData.value) {
        if (courseProgressChartRef.value && !courseProgressChart) {
          initCourseProgressChart()
        }
        
        // 确保有直方图数据才初始化
        if (recentScoresChartRef.value && !recentScoresChart && statistics.recentQuestionScores && statistics.recentQuestionScores.length > 0) {
          console.log('准备初始化直方图...')
          initRecentScoresChart()
        } else {
          console.warn('跳过直方图初始化，数据:', statistics.recentQuestionScores)
        }
        
        if (trendChartRef.value && !trendChart) {
          initTrendChart()
        }
        console.log('图表初始化完成')
      } else {
        console.warn('没有数据，图表初始化跳过')
      }
    } catch (e) {
      console.error('图表初始化失败:', e)
    }
  }, 1200) // 延迟增加到1.2秒
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.level-analysis {
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #f1f5f9 100%);
  min-height: calc(100vh - 80px);
  position: relative;
}

/* 标题样式 */
.page-header {
  margin-bottom: 25px;
}

.title-gradient {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
  letter-spacing: 0.5px;
}

.title-gradient::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 50px;
  height: 3px;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  border-radius: 3px;
}

.analysis-card {
  margin-bottom: 20px;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.analysis-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  position: relative;
  padding-left: 15px;
}

.card-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: linear-gradient(to bottom, #3a7bd5, #00d2ff);
  border-radius: 2px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  border: none;
  border-radius: 6px;
  padding: 8px 15px;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 10px rgba(58, 123, 213, 0.3);
}

.refresh-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  transition: transform 0.5s ease;
}

.refresh-btn:hover .refresh-icon {
  transform: rotate(360deg);
}

/* 加载样式 */
.loading-container {
  min-height: 300px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.chart-loader {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.circle-pulse {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  animation: circlePulse 1.5s infinite ease-in-out;
}

.circle-pulse:nth-child(1) {
  animation-delay: 0s;
}

.circle-pulse:nth-child(2) {
  animation-delay: 0.3s;
}

.circle-pulse:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes circlePulse {
  0%, 100% {
    transform: scale(0.5);
    opacity: 0.3;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
}

.loading-text {
  color: #3a7bd5;
  font-size: 16px;
  font-weight: 500;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}

.charts-container {
  padding: 10px;
}

.chart-wrapper {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid #EBEEF5;
}

.chart-wrapper:hover {
  box-shadow: 0 5px 15px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #303133;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-icon {
  display: inline-block;
  width: 24px;
  height: 24px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.pie-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%233a7bd5"><path d="M11 2v20c-5.07-.5-9-4.79-9-10s3.93-9.5 9-10zm2.03 0v8.99H22c-.47-4.74-4.24-8.52-8.97-8.99zm0 11.01V22c4.74-.47 8.5-4.25 8.97-8.99h-8.97z"/></svg>');
}

.bar-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%233a7bd5"><path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z"/></svg>');
}

.trend-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%233a7bd5"><path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/></svg>');
}

.chart {
  height: 300px;
  width: 100%;
  position: relative;
  z-index: 1;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f8fafc;
  transition: all 0.3s ease;
}

.chart-wrapper:hover .chart {
  background-color: #f5f7fa;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.03);
}

.data-summary {
  margin-top: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #EBEEF5;
  transition: all 0.3s ease;
}

.data-summary:hover {
  box-shadow: 0 5px 15px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
}

.summary-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  padding-left: 15px;
}

.summary-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: linear-gradient(to bottom, #3a7bd5, #00d2ff);
  border-radius: 2px;
}

.custom-descriptions :deep(.el-descriptions__label) {
  font-weight: 600;
  padding: 15px;
  background-color: #f8fafc;
}

.custom-descriptions :deep(.el-descriptions__cell) {
  padding: 15px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #3a7bd5;
}

.score-value {
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-unit {
  color: #909399;
  font-size: 14px;
}

.course-name {
  color: #606266;
  font-weight: 500;
}

.efficiency-tag {
  padding: 5px 12px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 15px;
}

.empty-content {
  min-height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .custom-descriptions :deep(.el-descriptions__body) {
    overflow-x: auto;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .refresh-btn {
    align-self: flex-end;
  }
}
</style> 