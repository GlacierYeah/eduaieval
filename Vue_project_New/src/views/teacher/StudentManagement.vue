<template>
  <app-layout>
    <div class="student-management">
      <div class="page-header">
        <h2>学生管理</h2>
        <el-input
          v-model="searchQuery"
          placeholder="搜索学生"
          clearable
          prefix-icon="el-icon-search"
          style="width: 300px"
        ></el-input>
      </div>
      
      <el-table v-loading="loading" :data="filteredStudents" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="username" label="用户名"></el-table-column>
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.role === 'student' ? '学生' : '教师' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="课程数量" width="120">
          <template #default="scope">
            <span>{{ studentCourses[scope.row.id]?.length || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <!-- <el-button size="small" @click="viewStudentCourses(scope.row)">查看课程</el-button> -->
            <el-button size="small" type="primary" @click="viewStudentAnswers(scope.row)">查看答题</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 学生课程对话框 -->
      <el-dialog v-model="coursesDialogVisible" :title="`${currentStudent?.username || ''} 的课程`" width="600px">
        <div v-loading="coursesLoading">
          <el-empty v-if="!currentStudentCourses.length" description="该学生尚未加入任何课程"></el-empty>
          <el-table v-else :data="currentStudentCourses" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="title" label="课程名称"></el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewCourseDetails(scope.row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-dialog>
      
      <!-- 学生答题记录对话框 -->
      <el-dialog v-model="answersDialogVisible" :title="`${currentStudent ? currentStudent.username : ''} 的答题记录`" width="800px">
        <div v-loading="answersLoading">
          <el-empty v-if="!courseAnswers.length" description="该学生尚未提交任何答案">
            <template #description>
              <p>{{ answersError || '该学生尚未提交任何答案' }}</p>
            </template>
          </el-empty>
          
          <div v-else class="course-answers-container">
            <!-- 按课程分组显示 -->
            <div v-for="course in courseAnswers" :key="course.course_id" class="course-section">
              <div class="course-header">
                <h3 class="course-title">{{ course.course_title }}</h3>
                <div class="course-stats">
                  <el-tag type="info">总答题: {{ course.total_answers }}</el-tag>
                  <el-tag :type="getScoreTagType(course.average_score)">平均分: {{ course.average_score || 0 }}</el-tag>
                </div>
              </div>
              
              <!-- 该课程的答题记录 -->
              <div v-for="answer in course.answers" :key="answer.id" class="answer-item">
                <div class="answer-header">
                  <h4 class="question-title">{{ answer.question_content }}</h4>
                  <div class="answer-meta">
                    <el-tag :type="getScoreTagType(answer.score || 0)">得分: {{ answer.score || 0 }}</el-tag>
                    <span class="answer-date" v-if="answer.created_at">{{ formatDate(answer.created_at) }}</span>
                  </div>
                </div>
                <div class="answer-content">
                  <h4>学生答案:</h4>
                  <p>{{ answer.content || '无答案' }}</p>
                </div>
                <div class="feedback" v-if="answer.feedback">
                  <h4>评价反馈:</h4>
                  <p>{{ answer.feedback || '无反馈' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-dialog>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'

const router = useRouter()
const loading = ref(false)
const students = ref([])
const searchQuery = ref('')
const studentCourses = reactive({}) // 存储每个学生的课程数量

// 课程对话框
const coursesDialogVisible = ref(false)
const coursesLoading = ref(false)
const currentStudent = ref(null)
const currentStudentCourses = ref([])

// 答题对话框
const answersDialogVisible = ref(false)
const answersLoading = ref(false)
const courseAnswers = ref([]) // 学生答题记录
const answersError = ref('')

// 过滤学生列表
const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(student => 
    student.username.toLowerCase().includes(query)
  )
})

// 获取学生列表
const fetchStudents = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/students')
    students.value = response.data.students || []
    
    // 获取每个学生的课程数量
    for (const student of students.value) {
      fetchStudentCourseCount(student.id)
    }
  } catch (error) {
    console.error('获取学生列表失败', error)
    ElMessage.error('获取学生列表失败')
  } finally {
    loading.value = false
  }
}

// 获取学生的课程数量
const fetchStudentCourseCount = async (studentId) => {
  try {
    const response = await axios.get(`/api/students/${studentId}/courses`)
    studentCourses[studentId] = response.data.courses || []
  } catch (error) {
    console.error(`获取学生${studentId}的课程数量失败`, error)
  }
}

// 查看学生课程
const viewStudentCourses = async (student) => {
  currentStudent.value = student
  coursesDialogVisible.value = true
  coursesLoading.value = true
  
  try {
    const response = await axios.get(`/api/students/${student.id}/courses`)
    currentStudentCourses.value = response.data.courses || []
  } catch (error) {
    console.error('获取学生课程失败', error)
    ElMessage.error('获取学生课程失败')
  } finally {
    coursesLoading.value = false
  }
}

// 查看课程详情
const viewCourseDetails = (course) => {
  router.push(`/courses/${course.id}`)
}

// 查看学生答题记录
const viewStudentAnswers = async (student) => {
  currentStudent.value = student
  answersDialogVisible.value = true
  answersLoading.value = true
  courseAnswers.value = [] // 清空之前的数据
  answersError.value = '' // 清空错误信息
  
  try {
    console.log(`正在获取学生(ID:${student.id})的答题记录...`)
    const response = await axios.get(`/api/students/${student.id}/answers`)
    console.log('学生答题记录API响应:', response.data)
    
    if (response.data.success) {
      // 处理按课程分组的答题记录
      if (response.data.courses && Array.isArray(response.data.courses)) {
        // 过滤掉没有答题记录的课程
        const coursesWithAnswers = response.data.courses.filter(
          course => course.answers && Array.isArray(course.answers) && course.answers.length > 0
        )
        
        if (coursesWithAnswers.length > 0) {
          courseAnswers.value = coursesWithAnswers
          console.log(`成功获取到${coursesWithAnswers.length}门课程的答题记录`)
        } else {
          answersError.value = '该学生尚未提交任何答案'
        }
      } else {
        console.warn('API返回的数据中没有courses数组或格式不正确')
        answersError.value = '返回的答题记录格式不正确'
      }
    } else {
      console.error(`API返回错误:`, response.data.message)
      answersError.value = response.data.message || '获取学生答题记录失败'
      ElMessage.error(response.data.message || '获取学生答题记录失败')
    }
  } catch (error) {
    console.error('获取学生答题记录失败', error)
    
    if (error.response) {
      console.error('响应状态码:', error.response.status)
      console.error('响应数据:', error.response.data)
      const errorMessage = error.response.data && error.response.data.message 
        ? error.response.data.message 
        : error.message
      answersError.value = `获取答题记录失败: ${errorMessage}`
      ElMessage.error(`获取答题记录失败: ${errorMessage}`)
    } else if (error.request) {
      console.error('请求已发送但没有收到响应')
      answersError.value = '服务器无响应，请检查网络连接'
      ElMessage.error('服务器无响应，请检查网络连接')
    } else {
      console.error('请求配置出错:', error.message)
      answersError.value = `请求错误: ${error.message}`
      ElMessage.error(`请求错误: ${error.message}`)
    }
  } finally {
    answersLoading.value = false
  }
}

// 根据分数获取标签类型
const getScoreTagType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchStudents()
})
</script>

<style scoped>
.student-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.course-answers-container {
  margin-top: 10px;
}

.course-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.course-title {
  font-weight: bold;
  font-size: 16px;
}

.course-stats {
  display: flex;
  gap: 10px;
}

.ml-10 {
  margin-left: 10px;
}

.answer-item {
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #EBEEF5;
}

.question-title {
  margin: 0;
  font-size: 15px;
  color: #303133;
  max-width: 70%;
}

.answer-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.answer-date {
  font-size: 12px;
  color: #909399;
}

.answer-content, .feedback {
  margin-bottom: 10px;
}

.answer-content h4, .feedback h4 {
  margin: 0 0 5px 0;
  color: #606266;
  font-size: 14px;
}

.answer-content p, .feedback p {
  margin: 0;
  white-space: pre-wrap;
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.course-section {
  margin-bottom: 25px;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  padding: 15px;
  background-color: #fafafa;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  margin-bottom: 15px;
  border-bottom: 1px solid #EBEEF5;
}

.course-stats {
  display: flex;
  gap: 10px;
}

.course-title {
  margin: 0;
  font-weight: bold;
  color: #303133;
}
</style> 