<template>
  <app-layout>
    <div class="course-detail" v-loading="loading">
      <template v-if="course">
        <div class="course-header animate__animated animate__fadeInDown">
          <div class="course-title">
            <h2 class="title-gradient">{{ course.title }}</h2>
            <el-tag class="teacher-tag">{{ course.teachers?.join(', ') }}</el-tag>
          </div>
          <el-button @click="router.back()" class="back-button">
            <i class="back-icon"></i>返回
          </el-button>
        </div>
        
        <div class="course-meta animate__animated animate__fadeIn animate__delay-1s">
          <div class="course-image-container">
            <div class="course-image">
              <img v-if="course.image_path" :src="getImageUrl(course.image_path)" alt="课程图片" />
              <div v-else class="no-image">
                <el-icon><el-icon-picture /></el-icon>
              </div>
            </div>
            <div class="image-reflection"></div>
          </div>
          <div class="course-info">
            <p class="course-description">{{ course.description }}</p>
            <div class="course-statistics">
              <div class="stat-item">
                <i class="stat-icon student-icon"></i>
                <div class="stat-data">
                  <span class="stat-value">{{ course.students_count }}</span>
                  <span class="stat-label">学生数量</span>
                </div>
              </div>
              <div class="stat-item">
                <i class="stat-icon question-icon"></i>
                <div class="stat-data">
                  <span class="stat-value">{{ course.questions_count }}</span>
                  <span class="stat-label">问题数量</span>
                </div>
              </div>
            </div>
            <div class="action-buttons animate__animated animate__fadeInUp animate__delay-2s">
              <el-button 
                type="primary" 
                v-if="course.file_path" 
                @click="downloadFile" 
                size="large" 
                icon="Download"
                class="action-btn download-btn"
              >
                下载课程文件
              </el-button>
              <el-button 
                type="success" 
                @click="goToAiChat" 
                size="large" 
                icon="ChatDotRound"
                class="action-btn chat-btn"
              >
                AI数字人答题
              </el-button>
            </div>
          </div>
        </div>
        
        <el-tabs class="course-tabs animate__animated animate__fadeInUp animate__delay-1s">
          <el-tab-pane label="知识图谱">
            <div class="knowledge-graph-header">
              <h3>课程知识结构</h3>
              <div class="view-toggle">
                <el-radio-group v-model="graphViewMode" size="small">
                  <el-radio-button label="graph">图谱视图</el-radio-button>
                  <el-radio-button label="list">列表视图</el-radio-button>
                </el-radio-group>
              </div>
            </div>
            
            <div v-if="knowledgeGraph">
              <div v-show="graphViewMode === 'graph'" class="knowledge-graph-container">
                <div class="graph-loading" v-if="graphViewMode === 'graph'">
                  <div class="nodes-pulse"></div>
                </div>
                <knowledge-graph-view :data="knowledgeGraph" />
              </div>
              
              <div v-show="graphViewMode === 'list'" class="knowledge-list-container">
                <knowledge-list-view :data="knowledgeGraph" />
              </div>
            </div>
            <el-empty v-else description="暂无知识图谱"></el-empty>
          </el-tab-pane>
          <el-tab-pane label="问题与练习">
            <div v-if="questions.length > 0" class="questions-container">
              <div 
                v-for="(question, index) in questions" 
                :key="question.id" 
                class="question-item animate__animated animate__fadeInUp"
                :style="{ animationDelay: `${index * 0.1}s` }"
              >
                <div class="question-header">
                  <h3>问题 {{ index + 1 }}:</h3>
                  <el-button 
                    v-if="userAnswers[question.id]" 
                    size="small" 
                    :type="getScoreButtonType(userAnswers[question.id].score)"
                    class="score-button"
                  >
                    得分: {{ userAnswers[question.id].score }}
                  </el-button>
                </div>
                
                <p class="question-content">{{ question.content }}</p>
                
                <div v-if="!userAnswers[question.id]" class="answer-section">
                  <el-input
                    v-model="answerInputs[question.id]"
                    type="textarea"
                    rows="4"
                    placeholder="请输入您的答案..."
                    class="answer-input"
                  ></el-input>
                  <el-button 
                    type="primary" 
                    :loading="submittingAnswer === question.id"
                    @click="submitAnswer(question)"
                    class="submit-button"
                  >
                    提交答案
                  </el-button>
                </div>
                
                <div v-else class="evaluation-result">
                  <div class="user-answer">
                    <h4>您的答案:</h4>
                    <p>{{ userAnswers[question.id].content }}</p>
                  </div>
                  <div class="feedback">
                    <h4>评价反馈:</h4>
                    <p>{{ userAnswers[question.id].feedback }}</p>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无问题"></el-empty>
          </el-tab-pane>
        </el-tabs>
      </template>
      <el-empty v-else description="课程不存在或已被删除"></el-empty>
    </div>
    
    <!-- 自定义加载动画 -->
    <div v-if="loading" class="custom-loader">
      <div class="loader-book">
        <div class="book-page"></div>
        <div class="book-page"></div>
        <div class="book-page"></div>
      </div>
      <p class="loader-text">加载课程内容...</p>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import KnowledgeGraphView from '../../components/KnowledgeGraphView.vue'
import KnowledgeListView from '../../components/KnowledgeListView.vue'
import AppLayout from '../../components/AppLayout.vue'
import { Download, ChatDotRound } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params.id)

const loading = ref(false)
const course = ref(null)
const knowledgeGraph = ref(null)
const questions = ref([])
const answerInputs = reactive({})
const userAnswers = reactive({})
const submittingAnswer = ref(null)
const graphViewMode = ref('graph') // 知识图谱展示模式：graph 或 list

// 获取课程详情
const fetchCourse = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/courses/${courseId.value}`)
    course.value = response.data.course
    
    // 稍微延迟关闭加载状态以便展示动画
    setTimeout(() => {
      loading.value = false
    }, 800)
  } catch (error) {
    console.error('获取课程详情失败', error)
    ElMessage.error('获取课程详情失败')
    loading.value = false
  }
}

// 获取知识图谱
const fetchKnowledgeGraph = async () => {
  try {
    const response = await axios.get(`/api/courses/${courseId.value}/knowledge_graph`)
    knowledgeGraph.value = response.data.knowledge_graph
  } catch (error) {
    console.error('获取知识图谱失败', error)
    ElMessage.error('获取知识图谱失败')
  }
}

// 获取问题列表
const fetchQuestions = async () => {
  try {
    const response = await axios.get(`/api/courses/${courseId.value}/questions`)
    questions.value = response.data.questions
    
    // 获取用户的答案历史
    await fetchUserAnswers()
  } catch (error) {
    console.error('获取问题列表失败', error)
    ElMessage.error('获取问题列表失败')
  }
}

// 获取用户的答案历史
const fetchUserAnswers = async () => {
  try {
    const response = await axios.get(`/api/courses/${courseId.value}/my-answers`)
    
    // 将用户答案整理到reactive对象中
    if (response.data.answers) {
      response.data.answers.forEach(answer => {
        userAnswers[answer.question_id] = answer
      })
    }
  } catch (error) {
    console.error('获取答案历史失败', error)
  }
}

// 提交答案
const submitAnswer = async (question) => {
  const answer = answerInputs[question.id]
  
  if (!answer || answer.trim() === '') {
    ElMessage.warning('请输入答案后提交')
    return
  }
  
  submittingAnswer.value = question.id
  
  try {
    const response = await axios.post(`/questions/${question.id}/answer`, {
      answer: answer
    })
    
    if (response.data.success) {
      ElMessage.success('答案提交成功')
      
      // 更新本地答案状态
      userAnswers[question.id] = {
        content: answer,
        score: response.data.evaluation.score,
        feedback: response.data.evaluation.feedback,
        id: response.data.answer_id
      }
      
      // 清空输入
      answerInputs[question.id] = ''
    } else {
      ElMessage.error(response.data.message || '答案提交失败')
    }
  } catch (error) {
    console.error('提交答案失败', error)
    ElMessage.error('提交答案失败')
  } finally {
    submittingAnswer.value = null
  }
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  return `http://localhost:5000/static/uploads/${path}`
}

// 下载课程文件
const downloadFile = () => {
  if (!course.value || !course.value.file_path) return
  
  const fileUrl = `http://localhost:5000/static/uploads/${course.value.file_path}`
  window.open(fileUrl, '_blank')
}

// 根据分数获取按钮类型
const getScoreButtonType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

// 跳转到AI数字人答题页面
const goToAiChat = () => {
  console.log('跳转到AI数字人答题页面，课程ID:', courseId.value)
  router.push(`/ai-assistant/${courseId.value}`)
}

onMounted(async () => {
  // 设置Animate.css的动画持续时间
  document.documentElement.style.setProperty('--animate-duration', '0.8s')
  
  await fetchCourse()
  await Promise.all([fetchKnowledgeGraph(), fetchQuestions()])
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.course-detail {
  padding: 20px;
  position: relative;
  background: linear-gradient(135deg, #f8f9fa 0%, #f1f5f9 100%);
  min-height: calc(100vh - 80px);
}

/* 标题样式 */
.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  padding: 20px 25px;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.8);
  position: relative;
}

.title-gradient {
  margin: 0 0 10px 0;
  color: transparent;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  -webkit-background-clip: text;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.5px;
  position: relative;
}

.teacher-tag {
  font-size: 14px;
  padding: 5px 12px;
  background: linear-gradient(45deg, rgba(58, 123, 213, 0.8), rgba(0, 210, 255, 0.8));
  color: white;
  border: none;
  border-radius: 20px;
  font-weight: 500;
  box-shadow: 0 3px 8px rgba(58, 123, 213, 0.2);
  transition: all 0.3s ease;
}

.teacher-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(58, 123, 213, 0.3);
}

.back-button {
  position: relative;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e0e6ed;
  background: white;
  color: #606266;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.back-button:hover {
  transform: translateX(-5px);
  background: #f5f7fa;
}

.back-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23606266"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  transition: transform 0.3s ease;
}

.back-button:hover .back-icon {
  transform: translateX(-3px);
}

/* 课程元数据 */
.course-meta {
  display: flex;
  margin-bottom: 30px;
  gap: 30px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.8);
  position: relative;
}

.course-image-container {
  position: relative;
  width: 320px;
  flex-shrink: 0;
}

.course-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 2;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s ease;
}

.course-image:hover img {
  transform: scale(1.1);
}

.image-reflection {
  position: absolute;
  bottom: -20px;
  left: 10%;
  width: 80%;
  height: 40px;
  background: rgba(0, 0, 0, 0.1);
  filter: blur(10px);
  border-radius: 50%;
  z-index: 1;
  transition: all 0.7s ease;
}

.course-image:hover + .image-reflection {
  width: 90%;
  left: 5%;
  opacity: 0.7;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #909399;
  font-size: 50px;
  border-radius: 12px;
}

.course-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.course-description {
  margin: 0 0 20px 0;
  color: #606266;
  line-height: 1.8;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.5);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  border-left: 3px solid #3a7bd5;
}

.course-statistics {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  background: white;
}

.stat-icon {
  display: inline-block;
  width: 40px;
  height: 40px;
  margin-right: 15px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.student-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%233a7bd5"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>');
}

.question-icon {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2300d2ff"><path d="M19 2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h4l3 3 3-3h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-6 16h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 11.9 13 12.5 13 14h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>');
}

.stat-data {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 3px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.action-btn {
  flex: 1;
  height: 50px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.7s ease;
}

.action-btn:hover::before {
  left: 100%;
}

.action-btn:hover {
  transform: translateY(-5px);
  letter-spacing: 1px;
}

.download-btn {
  background: linear-gradient(45deg, #3a7bd5, #00d2ff) !important;
  border: none !important;
  box-shadow: 0 5px 15px rgba(58, 123, 213, 0.3);
}

.download-btn:hover {
  box-shadow: 0 8px 20px rgba(58, 123, 213, 0.4);
}

.chat-btn {
  background: linear-gradient(45deg, #67C23A, #2E8B57) !important;
  border: none !important;
  box-shadow: 0 5px 15px rgba(46, 139, 87, 0.3);
}

.chat-btn:hover {
  box-shadow: 0 8px 20px rgba(46, 139, 87, 0.4);
}

/* 标签页样式 */
.course-tabs {
  margin-top: 30px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.course-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  height: 50px;
  line-height: 50px;
  transition: all 0.3s ease;
}

.course-tabs :deep(.el-tabs__item:hover) {
  color: #3a7bd5;
  transform: translateY(-2px);
}

.course-tabs :deep(.el-tabs__item.is-active) {
  color: #3a7bd5;
  font-weight: 600;
}

.course-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, #3a7bd5, #00d2ff);
}

.course-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e4e7ed;
}

.knowledge-graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid rgba(58, 123, 213, 0.1);
  padding-bottom: 15px;
}

.knowledge-graph-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  position: relative;
  padding-left: 15px;
}

.knowledge-graph-header h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 5px;
  height: 18px;
  background: linear-gradient(to bottom, #3a7bd5, #00d2ff);
  border-radius: 3px;
}

.view-toggle {
  display: flex;
  gap: 10px;
}

.knowledge-graph-container {
  height: 500px;
  border: 1px solid #EBEEF5;
  border-radius: 15px;
  padding: 15px;
  background-color: #ffffff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 25px;
  position: relative;
  overflow: hidden;
}

/* 图谱加载动画 */
.graph-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.5s ease;
}

.nodes-pulse {
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(58, 123, 213, 0.5) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}

.knowledge-list-container {
  padding: 25px;
  background-color: #ffffff;
  border-radius: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #EBEEF5;
  transition: all 0.3s ease;
}

.knowledge-list-container:hover {
  box-shadow: 0 5px 15px 0 rgba(0, 0, 0, 0.1);
}

/* 问题与练习样式 */
.questions-container {
  padding: 10px 0;
}

.question-item {
  padding: 25px;
  border: 1px solid #EBEEF5;
  border-radius: 15px;
  margin-bottom: 25px;
  background-color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  position: relative;
  overflow: hidden;
}

.question-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #3a7bd5, #00d2ff);
  border-radius: 4px 0 0 4px;
  opacity: 0.7;
}

.question-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 15px;
}

.question-header h3 {
  margin: 0;
  color: #3a7bd5;
  font-size: 18px;
  font-weight: 600;
}

.score-button {
  font-weight: 600;
  border-radius: 20px;
  padding: 8px 15px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.score-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.15);
}

.question-content {
  font-size: 16px;
  margin-bottom: 25px;
  padding: 18px;
  background-color: #f8fafc;
  border-radius: 10px;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.03);
  line-height: 1.7;
  border-left: 3px solid #3a7bd5;
  position: relative;
}

.answer-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.answer-input {
  transition: all 0.3s ease;
}

.answer-input:deep(.el-textarea__inner) {
  border-radius: 10px;
  padding: 15px;
  background-color: #f8fafc;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
  min-height: 120px !important;
  font-size: 15px;
  line-height: 1.6;
}

.answer-input:deep(.el-textarea__inner:focus) {
  border-color: #3a7bd5;
  box-shadow: 0 0 0 2px rgba(58, 123, 213, 0.2);
  background-color: #fff;
}

.submit-button {
  align-self: flex-end;
  padding: 10px 25px;
  font-size: 15px;
  border-radius: 8px;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  border: none;
  box-shadow: 0 4px 10px rgba(58, 123, 213, 0.3);
  transition: all 0.3s ease;
}

.submit-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(58, 123, 213, 0.4);
  letter-spacing: 1px;
}

.evaluation-result {
  background-color: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #eaeaea;
  transition: all 0.3s ease;
}

.evaluation-result:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  transform: translateY(-5px);
}

.user-answer, .feedback {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eaeaea;
}

.user-answer:last-child, .feedback:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.user-answer h4, .feedback h4 {
  margin: 0 0 12px 0;
  color: #409EFF;
  font-size: 16px;
  font-weight: 600;
  position: relative;
  padding-left: 15px;
}

.user-answer h4::before, .feedback h4::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  border-radius: 2px;
}

.user-answer h4::before {
  background-color: #409EFF;
}

.feedback h4 {
  color: #67C23A;
}

.feedback h4::before {
  background-color: #67C23A;
}

.user-answer p, .feedback p {
  margin: 0;
  color: #606266;
  line-height: 1.7;
  padding: 10px 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
}

/* 自定义加载动画 */
.custom-loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loader-book {
  width: 80px;
  height: 100px;
  position: relative;
  perspective: 500px;
}

.book-page {
  position: absolute;
  width: 80px;
  height: 100px;
  background: linear-gradient(45deg, #3a7bd5, #00d2ff);
  border-radius: 5px;
  transform-origin: left center;
  animation: pageFlip 1.5s infinite ease-in-out;
}

.book-page:nth-child(1) {
  animation-delay: 0s;
}

.book-page:nth-child(2) {
  animation-delay: 0.25s;
}

.book-page:nth-child(3) {
  animation-delay: 0.5s;
}

@keyframes pageFlip {
  0%, 100% {
    transform: rotateY(0deg);
  }
  50% {
    transform: rotateY(-180deg);
  }
}

.loader-text {
  margin-top: 25px;
  font-size: 18px;
  color: #3a7bd5;
  font-weight: 500;
  letter-spacing: 1px;
  animation: pulse 1.5s infinite;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .course-meta {
    flex-direction: column;
  }
  
  .course-image-container {
    width: 100%;
  }
  
  .course-image {
    height: 250px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .course-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .stat-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style> 