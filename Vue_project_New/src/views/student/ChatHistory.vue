<template>
  <app-layout>
    <div class="chat-history">
      <div class="page-header animate__animated animate__fadeInDown">
        <h2 class="title-gradient">对话记录</h2>
        <div class="filter-bar animate__animated animate__fadeInRight animate__delay-1s">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="filterByDate"
            class="date-picker-animated"
          ></el-date-picker>
        </div>
      </div>
      
      <div class="content-area">
        <div v-if="loading" class="loader-container">
          <div class="chat-loader">
            <div class="bubble"></div>
            <div class="bubble"></div>
            <div class="bubble"></div>
          </div>
          <p class="loading-text">加载对话记录中...</p>
        </div>
        
        <template v-else-if="courseConversations.length > 0">
          <div class="conversations-container">
            <el-card 
              v-for="(conversation, index) in filteredConversations" 
              :key="conversation.courseId"
              class="conversation-card animate__animated animate__fadeInUp"
              :style="{ animationDelay: `${index * 0.1}s` }"
              shadow="hover"
            >
              <div class="card-header">
                <div class="course-info">
                  <h3 class="course-title">{{ conversation.courseTitle }}</h3>
                  <div class="meta-info">
                    <div class="meta-item">
                      <el-icon><Calendar /></el-icon>
                      <span>{{ formatDate(conversation.latestTimestamp) }}</span>
                    </div>
                    <div class="meta-item">
                      <el-icon><Collection /></el-icon>
                      <span>{{ conversation.answersCount }} 个问题</span>
                    </div>
                  </div>
                </div>
                <div class="score-display">
                  <div class="score-circle" :data-score="conversation.averageScore">
                    <el-progress 
                      type="dashboard" 
                      :percentage="conversation.averageScore" 
                      :color="getScoreColor(conversation.averageScore)"
                      :stroke-width="8"
                      :width="80"
                    >
                      <template #default="{ percentage }">
                        <span class="progress-value">{{ percentage }}</span>
                      </template>
                    </el-progress>
                  </div>
                  <div class="score-info">
                    <span class="score-value">{{ conversation.averageScore }}</span>
                    <span class="score-label">平均分</span>
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <el-button 
                  type="primary" 
                  @click="openConversationDetails(conversation)"
                  icon="View"
                  class="detail-btn shine-effect"
                >
                  查看详情
                </el-button>
              </div>
            </el-card>
          </div>
        </template>
        <el-empty 
          v-else-if="!loading" 
          description="暂无对话历史记录"
          :image-size="200"
          class="animate__animated animate__fadeIn"
        ></el-empty>
      </div>
    </div>
    
    <!-- 对话详情对话框 -->
    <el-dialog 
      v-model="detailsDialogVisible" 
      :title="currentConversation ? currentConversation.courseTitle + ' 对话详情' : '对话详情'" 
      width="800px"
      destroy-on-close
      top="5vh"
      class="dialog-fade"
    >
      <div v-if="currentConversation" class="conversation-details">
        <div class="details-header animate__animated animate__fadeInDown">
          <div class="summary">
            <div class="summary-item pulse-in">
              <div class="summary-value">{{ currentConversation.averageScore }}</div>
              <div class="summary-label">总分数</div>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item pulse-in" style="animation-delay: 0.2s">
              <div class="summary-value">{{ currentConversation.answersCount }}</div>
              <div class="summary-label">问题数</div>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item pulse-in" style="animation-delay: 0.4s">
              <div class="summary-value date-value">{{ formatDate(currentConversation.latestTimestamp) }}</div>
              <div class="summary-label">日期</div>
            </div>
          </div>
        </div>
        
        <div class="qa-records">
          <div 
            v-for="(record, index) in currentConversation.answers" 
            :key="record.id" 
            class="qa-record animate__animated animate__fadeInUp"
            :style="{ animationDelay: `${index * 0.15}s` }"
          >
            <div class="record-header">
              <div class="question-info">
                <span class="question-number">问题 {{ index + 1 }}</span>
                <span class="question-id">#{{ record.question_id }}</span>
              </div>
              <el-tag 
                size="large" 
                :type="getScoreType(record.score)" 
                effect="dark" 
                class="score-tag glow-effect"
              >
                得分: {{ record.score }}
              </el-tag>
            </div>
            
            <div class="qa-content">
              <div class="question slide-in-left">
                <div class="content-header">
                  <h4><i class="dialog-icon question-icon"></i>问题内容</h4>
                </div>
                <div class="content-body question-content-body">
                  <p v-if="record.question_content && record.question_content !== '问题内容加载失败'">{{ record.question_content }}</p>
                  <p v-else class="empty-content">
                    <el-icon v-if="loading"><Loading /></el-icon>
                    {{ loading ? '正在加载问题内容...' : '暂无问题内容' }}
                  </p>
                </div>
              </div>
              <div class="answer slide-in-right">
                <div class="content-header">
                  <h4><i class="dialog-icon answer-icon"></i>我的回答</h4>
                </div>
                <div class="content-body">
                  <p>{{ record.content || record.answer }}</p>
                </div>
              </div>
              <div class="feedback slide-in-bottom">
                <div class="content-header">
                  <h4><i class="dialog-icon feedback-icon"></i>AI评价</h4>
                </div>
                <div class="content-body">
                  <p>{{ record.feedback }}</p>
                </div>
                <div class="feedback-score" :class="getScoreClass(record.score)">
                  <span>{{ getScoreLevel(record.score) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </app-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, Collection, View, Loading } from '@element-plus/icons-vue'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'

// 状态变量
const loading = ref(false)
const chatRecords = ref([])
const dateRange = ref(null)
const detailsDialogVisible = ref(false)
const currentConversation = ref(null)

// 获取对话记录
const fetchChatRecords = async () => {
  loading.value = true
  try {
    // 先获取所有课程
    const coursesResponse = await axios.get('/api/courses')
    const userCourses = coursesResponse.data.courses || []
    
    // 收集所有课程的回答
    const allAnswers = []
    
    // 对每个课程获取答题记录
    for (const course of userCourses) {
      try {
        const response = await axios.get(`/api/courses/${course.id}/my-answers`)
        if (response.data.success && response.data.answers) {
          // 获取该课程的所有问题详情
          const questionsResponse = await axios.get(`/api/courses/${course.id}/questions`)
          const questions = questionsResponse.data.questions || []
          
          // 创建问题ID到问题内容的映射
          const questionMap = {}
          questions.forEach(q => {
            questionMap[q.id] = q.content
          })
          
          // 添加课程信息到答案中
          const answersWithCourse = response.data.answers.map(answer => ({
            ...answer,
            course_id: course.id,
            course_title: course.title,
            // 确保答案有时间戳
            timestamp: answer.timestamp || answer.created_at || new Date().toISOString(),
            // 从问题映射中获取问题内容
            question_content: questionMap[answer.question_id] || '问题内容加载失败'
          }))
          allAnswers.push(...answersWithCourse)
        }
      } catch (error) {
        console.error(`获取课程 ${course.id} 的答题记录失败`, error)
      }
    }
    
    // 更新记录数组
    chatRecords.value = allAnswers
    
    // 延迟关闭加载状态，让动画效果更明显
    setTimeout(() => {
      loading.value = false
    }, 800)
    
  } catch (error) {
    console.error('获取对话记录失败', error)
    ElMessage.error('获取对话记录失败')
    loading.value = false
  }
}

// 按日期筛选
const filterByDate = () => {
  console.log('筛选日期:', dateRange.value)
}

// 格式化日期
const formatDate = (timestamp) => {
  if (!timestamp) return '未知时间'
  const date = new Date(timestamp)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

// 根据分数获取标签颜色
const getScoreType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

// 获取分数级别文字
const getScoreLevel = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 60) return '及格'
  return '需努力'
}

// 获取分数对应的CSS类
const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

// 获取进度条颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a' 
  if (score >= 80) return '#85ce61'
  if (score >= 70) return '#e6a23c'
  if (score >= 60) return '#f56c6c'
  return '#f56c6c'
}

// 将答题记录按课程分组
const courseConversations = computed(() => {
  const groupedByCourse = {}
  
  chatRecords.value.forEach(record => {
    const courseId = record.course_id
    if (!groupedByCourse[courseId]) {
      groupedByCourse[courseId] = {
        courseId: courseId,
        courseTitle: record.course_title,
        answers: [],
        totalScore: 0,
        latestTimestamp: record.timestamp
      }
    }
    
    // 添加答案
    groupedByCourse[courseId].answers.push(record)
    
    // 累加分数
    groupedByCourse[courseId].totalScore += record.score || 0
    
    // 更新最新时间戳
    if (new Date(record.timestamp) > new Date(groupedByCourse[courseId].latestTimestamp)) {
      groupedByCourse[courseId].latestTimestamp = record.timestamp
    }
  })
  
  // 计算每个课程的平均分和答案数量
  const result = Object.values(groupedByCourse).map(group => {
    const answersCount = group.answers.length
    const averageScore = answersCount > 0 ? Math.round(group.totalScore / answersCount) : 0
    
    return {
      ...group,
      answersCount,
      averageScore
    }
  })
  
  return result
})

// 筛选后的记录
const filteredConversations = computed(() => {
  let result = [...courseConversations.value]
  
  // 按日期筛选
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const startDate = dateRange.value[0].getTime()
    const endDate = dateRange.value[1].getTime()
    result = result.filter(conversation => {
      const recordDate = new Date(conversation.latestTimestamp).getTime()
      return recordDate >= startDate && recordDate <= endDate
    })
  }
  
  // 按时间倒序排列，最新的在前
  return result.sort((a, b) => new Date(b.latestTimestamp) - new Date(a.latestTimestamp))
})

// 打开对话详情
const openConversationDetails = (conversation) => {
  currentConversation.value = conversation
  detailsDialogVisible.value = true
}

// 页面加载时获取数据
onMounted(() => {
  fetchChatRecords()
  
  // 设置Animate.css的动画持续时间
  document.documentElement.style.setProperty('--animate-duration', '0.8s')
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.chat-history {
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  min-height: calc(100vh - 100px);
  position: relative;
  overflow: hidden;
}

/* 动态背景效果 */
.chat-history::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 20%, rgba(94, 114, 235, 0.1), transparent 25%),
    radial-gradient(circle at 80% 50%, rgba(0, 210, 255, 0.07), transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(138, 43, 226, 0.05), transparent 40%);
  z-index: 0;
  pointer-events: none;
  animation: backgroundPulse 20s infinite alternate ease-in-out;
}

@keyframes backgroundPulse {
  0% { opacity: 0.5; }
  50% { opacity: 0.7; }
  100% { opacity: 0.5; }
}

/* 添加动态波浪背景 */
.chat-history::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 100%;
  height: 150px;
  background-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 0v46.29c47.79 22.2 103.59 32.17 158 28 70.36-5.37 136.33-33.31 206.8-37.5 73.84-4.36 147.54 16.88 218.2 35.26 69.27 18 138.3 24.88 209.4 13.08 36.15-6 69.85-17.84 104.45-29.34C989.49 25 1113-14.29 1200 52.47V0z" opacity=".15" fill="%235e72eb"/></svg>');
  background-size: cover;
  z-index: 0;
  pointer-events: none;
  opacity: 0.7;
  animation: waveMove 20s linear infinite;
}

@keyframes waveMove {
  0% { background-position-x: 0; }
  100% { background-position-x: 1200px; }
}

/* 标题样式 */
.page-header {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
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
  width: 60px;
  height: 3px;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.page-header:hover .title-gradient::after {
  width: 100px;
}

.content-area {
  min-height: 300px;
  position: relative;
  z-index: 1;
}

.filter-bar {
  display: flex;
  gap: 10px;
}

.date-picker-animated {
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.date-picker-animated:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.08);
}

/* 对话记录卡片样式 */
.conversations-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 25px;
}

.conversation-card {
  border-radius: 18px;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  position: relative;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
  transform-style: preserve-3d;
  perspective: 1000px;
}

.conversation-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(94, 114, 235, 0.08) 0%, rgba(0, 210, 255, 0.08) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: 0;
}

.conversation-card:hover {
  transform: translateY(-15px) scale(1.02) rotateX(2deg);
  box-shadow: 0 20px 40px rgba(94, 114, 235, 0.18);
}

.conversation-card:hover::before {
  opacity: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  padding: 20px 25px 15px;
  border-bottom: 1px solid rgba(94, 114, 235, 0.1);
  position: relative;
  z-index: 1;
}

.course-info {
  flex: 1;
}

.course-title {
  font-size: 20px;
  margin: 0 0 15px 0;
  color: #303133;
  transition: all 0.4s ease;
  font-weight: 600;
  position: relative;
  padding-left: 15px;
}

.course-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 5px;
  height: 20px;
  background: linear-gradient(to bottom, #5e72eb, #00d2ff);
  border-radius: 3px;
  transition: height 0.3s ease;
}

.conversation-card:hover .course-title {
  color: #5e72eb;
}

.conversation-card:hover .course-title::before {
  height: 28px;
}

.meta-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #606266;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  padding: 5px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.5);
}

.meta-item i, .meta-item .el-icon {
  color: #5e72eb;
  font-size: 18px;
  transition: transform 0.3s ease;
}

.conversation-card:hover .meta-item {
  background: rgba(94, 114, 235, 0.08);
  transform: translateX(5px);
}

.conversation-card:hover .meta-item i,
.conversation-card:hover .meta-item .el-icon {
  transform: scale(1.2);
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-left: 20px;
  position: relative;
  z-index: 2;
}

.score-circle {
  position: relative;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.conversation-card:hover .score-circle {
  transform: scale(1.15) rotateY(10deg);
}

.progress-value {
  font-weight: bold;
  font-size: 18px;
  color: #303133;
}

.score-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}

.score-value {
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: all 0.3s ease;
}

.conversation-card:hover .score-value {
  transform: scale(1.1);
}

.score-label {
  font-size: 12px;
  color: #909399;
  margin-top: 3px;
}

.card-footer {
  margin-top: 20px;
  padding: 0 25px 25px;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.detail-btn {
  width: 100%;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border: none;
  border-radius: 12px;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
}

.detail-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(94, 114, 235, 0.3);
  letter-spacing: 1px;
}

/* 高级闪光按钮效果 */
.shine-effect::before {
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
  transition: transform 0.7s ease;
  animation: shine 5s infinite;
}

@keyframes shine {
  0% {
    transform: translateX(-200%) rotate(30deg);
  }
  20%, 100% {
    transform: translateX(300%) rotate(30deg);
  }
}

/* 自定义加载动画 */
.loader-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  position: relative;
  z-index: 1;
}

.chat-loader {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  position: relative;
}

.bubble {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin: 0 10px;
  position: relative;
  animation: bubbleBounce 1.5s infinite ease-in-out;
}

.bubble:nth-child(1) {
  background: linear-gradient(135deg, #5e72eb, #8763fc);
  animation-delay: 0s;
  box-shadow: 0 5px 15px rgba(94, 114, 235, 0.4);
}

.bubble:nth-child(2) {
  background: linear-gradient(135deg, #7b85fd, #5e72eb);
  animation-delay: 0.3s;
  box-shadow: 0 5px 15px rgba(123, 133, 253, 0.4);
}

.bubble:nth-child(3) {
  background: linear-gradient(135deg, #00d2ff, #5e72eb);
  animation-delay: 0.6s;
  box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4);
}

@keyframes bubbleBounce {
  0%, 100% {
    transform: translateY(0) scale(1);
    box-shadow: 0 5px 15px rgba(94, 114, 235, 0.4);
  }
  50% {
    transform: translateY(-25px) scale(1.1);
    box-shadow: 0 20px 30px rgba(94, 114, 235, 0.2);
  }
}

.loading-text {
  color: #606266;
  font-size: 18px;
  font-weight: 500;
  animation: textPulse 1.5s infinite;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 10px rgba(94, 114, 235, 0.2);
}

@keyframes textPulse {
  0%, 100% {
    opacity: 0.7;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

/* 对话详情样式 */
.dialog-fade {
  --el-dialog-border-radius: 20px;
}

.dialog-fade :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(94, 114, 235, 0.1);
  padding: 20px 25px;
  margin-right: 0;
  background: linear-gradient(135deg, rgba(94, 114, 235, 0.03) 0%, rgba(0, 210, 255, 0.03) 100%);
}

.dialog-fade :deep(.el-dialog__title) {
  font-weight: 600;
  color: #303133;
  font-size: 20px;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dialog-fade :deep(.el-dialog__body) {
  padding: 25px;
}

.conversation-details {
  max-height: 70vh;
  overflow-y: auto;
  padding: 0 5px;
  scrollbar-width: thin;
}

.conversation-details::-webkit-scrollbar {
  width: 6px;
}

.conversation-details::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 10px;
}

.conversation-details::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #5e72eb, #00d2ff);
  border-radius: 10px;
}

.conversation-details::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #4a5dd6, #00c2eb);
}

.details-header {
  margin-bottom: 30px;
}

.summary {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f7 100%);
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 5px 20px rgba(94, 114, 235, 0.08);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.summary::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 20%, rgba(94, 114, 235, 0.05), transparent 25%),
    radial-gradient(circle at 80% 80%, rgba(0, 210, 255, 0.05), transparent 25%);
  z-index: 0;
  opacity: 0.8;
}

.summary-divider {
  width: 1px;
  height: 70px;
  background: linear-gradient(to bottom, transparent, rgba(94, 114, 235, 0.3), transparent);
}

.summary-item {
  text-align: center;
  flex: 1;
  position: relative;
  z-index: 1;
}

@keyframes pulseIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.pulse-in {
  animation: pulseIn 0.8s forwards cubic-bezier(0.34, 1.56, 0.64, 1);
}

.summary-label {
  font-size: 14px;
  color: #606266;
  margin-top: 10px;
  font-weight: 500;
}

.summary-value {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 10px rgba(94, 114, 235, 0.2);
  position: relative;
}

.summary-value::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border-radius: 3px;
}

.date-value {
  font-size: 22px;
}

.qa-records {
  margin-top: 30px;
}

.qa-record {
  border: 1px solid rgba(94, 114, 235, 0.1);
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 30px;
  background-color: white;
  box-shadow: 0 8px 20px rgba(94, 114, 235, 0.05);
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
  position: relative;
  overflow: hidden;
  transform-style: preserve-3d;
}

.qa-record:hover {
  transform: translateY(-8px) scale(1.01);
  box-shadow: 0 15px 30px rgba(94, 114, 235, 0.12);
}

.qa-record::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #5e72eb, #00d2ff);
  border-radius: 4px 0 0 4px;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(94, 114, 235, 0.1);
}

.question-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.question-number {
  font-weight: bold;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 20px;
  position: relative;
}

.question-id {
  font-size: 12px;
  color: #909399;
  opacity: 0.7;
  background: rgba(94, 114, 235, 0.1);
  padding: 3px 8px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.qa-record:hover .question-id {
  background: rgba(94, 114, 235, 0.2);
  transform: translateX(5px);
}

.score-tag {
  font-weight: bold;
  padding: 8px 16px;
  height: auto;
  line-height: 1;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

/* 发光效果 */
.glow-effect {
  position: relative;
}

.glow-effect::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.8) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  mix-blend-mode: overlay;
  border-radius: 20px;
}

.glow-effect:hover::after {
  opacity: 1;
  animation: rotate 2s infinite linear;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.qa-content {
  margin-top: 25px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.question, .answer, .feedback {
  position: relative;
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.qa-record:hover .question,
.qa-record:hover .answer,
.qa-record:hover .feedback {
  transform: translateZ(10px);
}

/* 内容滑入动画 */
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInBottom {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-in-left {
  animation: slideInLeft 0.6s forwards cubic-bezier(0.165, 0.84, 0.44, 1);
}

.slide-in-right {
  animation: slideInRight 0.6s forwards cubic-bezier(0.165, 0.84, 0.44, 1);
  animation-delay: 0.2s;
  opacity: 0;
}

.slide-in-bottom {
  animation: slideInBottom 0.6s forwards cubic-bezier(0.165, 0.84, 0.44, 1);
  animation-delay: 0.4s;
  opacity: 0;
}

.content-header {
  margin-bottom: 15px;
}

.content-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  position: relative;
}

.dialog-icon {
  display: inline-block;
  width: 28px;
  height: 28px;
  margin-right: 10px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  transition: transform 0.3s ease;
}

.qa-record:hover .dialog-icon {
  transform: scale(1.2) rotate(5deg);
}

.question-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%235e72eb"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-1-5h2v2h-2v-2zm2-1.645V14h-2v-1.5a1 1 0 0 1 1-1 1.5 1.5 0 1 0-1.471-1.794l-1.962-.393A3.501 3.501 0 1 1 13 13.355z"/></svg>');
}

.answer-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2310b981"><path d="M6.455 19L2 22.5V4a1 1 0 0 1 1-1h18a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H6.455zM4 18.385L5.763 17H20V5H4v13.385zM11 13h2v2h-2v-2zm0-6h2v5h-2V7z"/></svg>');
}

.feedback-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23f59e0b"><path d="M6.455 19L2 22.5V4a1 1 0 0 1 1-1h18a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H6.455zM4 18.385L5.763 17H20V5H4v13.385zM11 13h2v2h-2v-2zm0-6h2v5h-2V7z"/></svg>');
}

.content-body {
  background-color: #fafbfc;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(94, 114, 235, 0.05);
  transition: all 0.4s ease;
  border: 1px solid rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
}

.content-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, transparent 100%);
  z-index: 0;
}

.qa-record:hover .content-body {
  box-shadow: 0 8px 25px rgba(94, 114, 235, 0.1);
  transform: translateY(-5px);
}

.content-body p {
  margin: 0;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  position: relative;
  z-index: 1;
}

.question .content-body {
  background-color: rgba(94, 114, 235, 0.05);
  color: #5e72eb;
  border-left: 4px solid #5e72eb;
}

.answer .content-body {
  background-color: rgba(16, 185, 129, 0.05);
  color: #10b981;
  border-left: 4px solid #10b981;
}

.feedback .content-body {
  background-color: rgba(245, 158, 11, 0.05);
  color: #f59e0b;
  border-left: 4px solid #f59e0b;
}

.feedback-score {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 12px;
  padding: 8px 15px;
  border-radius: 25px;
  font-weight: bold;
  letter-spacing: 1px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-50%);
  transition: all 0.3s ease;
}

.qa-record:hover .feedback-score {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.question-content-body {
  min-height: 60px;
}

.empty-content {
  color: #909399;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-high {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.score-medium {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.score-low {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 额外添加的动画效果 */
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.el-empty {
  animation: fadeInScale 1s forwards cubic-bezier(0.165, 0.84, 0.44, 1);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .conversations-container {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .score-display {
    padding-left: 0;
  }
  
  .summary {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
  }
  
  .summary-divider {
    width: 80%;
    height: 1px;
  }
  
  .feedback-score {
    position: relative;
    top: 10px;
    right: auto;
    display: inline-block;
    margin-top: 15px;
    transform: none;
  }
  
  .qa-record:hover .feedback-score {
    transform: scale(1.05);
  }
}
</style> 