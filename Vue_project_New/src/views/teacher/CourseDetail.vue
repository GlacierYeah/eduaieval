<template>
  <app-layout>
    <div class="course-detail" v-loading="loading">
      <template v-if="course">
        <div class="course-header">
          <div class="course-title">
            <h2>{{ course.title }}</h2>
            <div class="course-meta-tags">
              <el-tag>{{ course.teachers?.join(', ') }}</el-tag>
              <el-tag type="success">学生: {{ course.students_count }}</el-tag>
              <el-tag type="warning">问题: {{ course.questions_count }}</el-tag>
            </div>
          </div>
          <div class="header-actions">
            <el-button @click="router.push('/course-management')">返回</el-button>
            <el-button type="primary" @click="showEditCourseDialog">编辑课程</el-button>
          </div>
        </div>
        
        <div class="course-content">
          <div class="course-sidebar">
            <div class="course-image">
              <img v-if="course.image_path" :src="getImageUrl(course.image_path)" alt="课程图片" />
              <div v-else class="no-image">
                <el-icon><el-icon-picture /></el-icon>
              </div>
            </div>
            
            <div class="course-actions">
              <el-button v-if="course.file_path" type="success" icon="el-icon-download" @click="downloadFile" style="width: 100%; margin-right: auto;">
                下载课程文件
              </el-button>
              
              <el-button type="danger" icon="el-icon-delete" @click="confirmDeleteCourse" style="width: 100%;margin-left: auto;">
                删除课程
              </el-button>
            </div>
          </div>
          
          <div class="course-main">
            <div class="course-description">
              <h3>课程描述</h3>
              <p>{{ course.description || '暂无描述' }}</p>
            </div>
            
            <el-tabs class="course-tabs">
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
                    <knowledge-graph-view :data="knowledgeGraph" />
                  </div>
                  
                  <div v-show="graphViewMode === 'list'" class="knowledge-list-container">
                    <knowledge-list-view :data="knowledgeGraph" />
                  </div>
                </div>
                <el-empty v-else description="暂无知识图谱数据"></el-empty>
              </el-tab-pane>
              
              <el-tab-pane label="问题管理">
                <div class="questions-management">
                  <div class="questions-header">
                    <h3>课程问题 ({{ questions.length }})</h3>
                    <el-button type="primary" size="small" @click="showAddQuestionDialog">
                      添加问题
                    </el-button>
                  </div>
                  
                  <el-table v-if="questions.length > 0" :data="questions" border style="width: 100%">
                    <!-- <el-table-column prop="id" label="ID" width="60"></el-table-column> -->
                    <el-table-column prop="content" label="问题内容" show-overflow-tooltip></el-table-column>
                    <el-table-column label="操作" width="150">
                      <template #default="scope">
                        <div style="display: flex;justify-content: space-between;align-items: center;width: 100%;">
                          <el-button size="small" @click="viewQuestion(scope.row)" style="margin-left: 0;">查看</el-button>
                          <el-button size="small" type="danger" @click="confirmDeleteQuestion(scope.row)" style="margin-left: 0;">删除</el-button>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table>
                  <el-empty v-else description="暂无问题"></el-empty>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="学生答题">
                <div class="student-answers">
                  <h3>学生答题情况</h3>
                  
                  <div v-if="studentAnswers.length > 0">
                    <el-collapse accordion>
                      <el-collapse-item v-for="answer in studentAnswers" :key="answer.id" :title="`${answer.student_name} - 得分: ${answer.score}`">
                        <div class="answer-details">
                          <div class="question-section">
                            <h4>问题:</h4>
                            <p>{{ answer.question_content }}</p>
                          </div>
                          <div class="answer-section">
                            <h4>学生答案:</h4>
                            <p>{{ answer.content }}</p>
                          </div>
                          <div class="feedback-section">
                            <h4>反馈:</h4>
                            <p>{{ answer.feedback }}</p>
                          </div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                  <el-empty v-else description="暂无学生答题记录"></el-empty>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </template>
      <el-empty v-else description="课程不存在或已被删除"></el-empty>
      
      <!-- 编辑课程对话框 -->
      <el-dialog v-model="editDialogVisible" title="编辑课程" width="600px">
        <el-form :model="editForm" label-width="100px">
          <el-form-item label="课程名称">
            <el-input v-model="editForm.title"></el-input>
          </el-form-item>
          <el-form-item label="课程描述">
            <el-input type="textarea" v-model="editForm.description" rows="4"></el-input>
          </el-form-item>
          <el-form-item label="更新图片">
            <el-upload
              class="avatar-uploader"
              action="#"
              :auto-upload="false"
              :on-change="handleImageChange"
              :show-file-list="false"
            >
              <img v-if="imageUrl" :src="imageUrl" class="avatar" />
              <img v-else-if="course && course.image_path" :src="getImageUrl(course.image_path)" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><el-icon-plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item label="更新文件">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
            >
              <el-button type="primary">选择文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF, DOCX 格式文件
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="submitting" @click="updateCourse">保存</el-button>
          </div>
        </template>
      </el-dialog>
      
      <!-- 添加问题对话框 -->
      <el-dialog v-model="addQuestionDialogVisible" title="添加问题" width="600px">
        <el-form :model="questionForm" label-width="100px">
          <el-form-item label="问题内容">
            <el-input type="textarea" v-model="questionForm.content" rows="4"></el-input>
          </el-form-item>
          <el-form-item label="参考答案">
            <el-input type="textarea" v-model="questionForm.reference_answer" rows="6"></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="addQuestionDialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="submitting" @click="addQuestion">添加</el-button>
          </div>
        </template>
      </el-dialog>
      
      <!-- 查看问题对话框 -->
      <el-dialog v-model="viewQuestionDialogVisible" title="问题详情" width="600px">
        <div v-if="currentQuestion" class="question-detail">
          <el-form :model="editQuestionForm" label-width="100px">
            <el-form-item label="问题内容:">
              <el-input 
                type="textarea" 
                v-model="editQuestionForm.content" 
                rows="4"
                :disabled="!isEditingQuestion"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="参考答案:">
              <el-input 
                type="textarea" 
                v-model="editQuestionForm.reference_answer" 
                rows="6"
                :disabled="!isEditingQuestion"
              ></el-input>
            </el-form-item>
          </el-form>
          
          <div class="question-actions">
            <el-button v-if="!isEditingQuestion" type="primary" @click="startEditQuestion">
              编辑
            </el-button>
            <template v-else>
              <el-button @click="cancelEditQuestion">取消</el-button>
              <el-button type="primary" :loading="submitting" @click="saveQuestion">
                保存
              </el-button>
            </template>
          </div>
        </div>
      </el-dialog>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import KnowledgeGraphView from '../../components/KnowledgeGraphView.vue'
import KnowledgeListView from '../../components/KnowledgeListView.vue'
import AppLayout from '../../components/AppLayout.vue'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params.id)

// 状态变量
const loading = ref(false)
const course = ref(null)
const knowledgeGraph = ref(null)
const questions = ref([])
const studentAnswers = ref([])
const submitting = ref(false)
const imageUrl = ref('')
const selectedFile = ref(null)
const graphViewMode = ref('graph') // 知识图谱展示模式：graph 或 list
const currentQuestion = ref(null)
const isEditingQuestion = ref(false)
const savingQuestion = ref(false)

// 对话框状态
const editDialogVisible = ref(false)
const addQuestionDialogVisible = ref(false)
const viewQuestionDialogVisible = ref(false)

// 表单数据
const editForm = reactive({
  title: '',
  description: '',
  image: null,
  file: null
})

const questionForm = reactive({
  content: '',
  reference_answer: ''
})

const editQuestionForm = reactive({
  content: '',
  reference_answer: ''
})

// 获取课程详情
const fetchCourse = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/courses/${courseId.value}`)
    course.value = response.data.course
    
    // 预填编辑表单
    editForm.title = course.value.title
    editForm.description = course.value.description
  } catch (error) {
    console.error('获取课程详情失败', error)
    ElMessage.error('获取课程详情失败')
  } finally {
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
  } catch (error) {
    console.error('获取问题列表失败', error)
    ElMessage.error('获取问题列表失败')
  }
}

// 获取学生答题情况
const fetchStudentAnswers = async () => {
  try {
    const response = await axios.get(`/api/courses/${courseId.value}/answers`)
    studentAnswers.value = response.data.answers || []
  } catch (error) {
    console.error('获取学生答题情况失败', error)
    ElMessage.error('获取学生答题情况失败')
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

// 显示编辑课程对话框
const showEditCourseDialog = () => {
  editDialogVisible.value = true
}

// 处理图片上传
const handleImageChange = (file) => {
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件')
    return
  }
  
  if (file.raw.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过 2MB')
    return
  }
  
  editForm.image = file.raw
  imageUrl.value = URL.createObjectURL(file.raw)
}

// 处理文件上传
const handleFileChange = (file) => {
  const isPDF = file.raw.name.endsWith('.pdf')
  const isDOCX = file.raw.name.endsWith('.docx') || file.raw.name.endsWith('.doc')
  
  if (!isPDF && !isDOCX) {
    ElMessage.error('请上传 PDF 或 DOCX 格式文件')
    return
  }
  
  if (file.raw.size / 1024 / 1024 > 10) {
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  
  editForm.file = file.raw
}

// 更新课程
const updateCourse = async () => {
  submitting.value = true
  
  try {
    const formData = new FormData()
    formData.append('title', editForm.title)
    formData.append('description', editForm.description)
    
    if (editForm.image) {
      formData.append('image', editForm.image)
    }
    
    if (editForm.file) {
      formData.append('file', editForm.file)
    }
    
    const response = await axios.put(`/courses/${courseId.value}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      ElMessage.success('课程更新成功')
      editDialogVisible.value = false
      await fetchCourse()
    } else {
      ElMessage.error(response.data.message || '课程更新失败')
    }
  } catch (error) {
    console.error('更新课程失败', error)
    ElMessage.error('更新课程失败')
  } finally {
    submitting.value = false
  }
}

// 删除课程
const confirmDeleteCourse = () => {
  ElMessageBox.confirm(`确定要删除课程 "${course.value.title}" 吗？此操作不可恢复。`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await axios.delete(`/courses/${courseId.value}`)
      if (response.data.success) {
        ElMessage.success('课程已删除')
        router.push('/course-management')
      } else {
        ElMessage.error(response.data.message || '删除课程失败')
      }
    } catch (error) {
      console.error('删除课程失败', error)
      ElMessage.error('删除课程失败')
    }
  }).catch(() => {})
}

// 显示添加问题对话框
const showAddQuestionDialog = () => {
  questionForm.content = ''
  questionForm.reference_answer = ''
  addQuestionDialogVisible.value = true
}

// 添加问题
const addQuestion = async () => {
  if (!questionForm.content || !questionForm.reference_answer) {
    ElMessage.warning('请填写完整问题和参考答案')
    return
  }
  
  submitting.value = true
  
  try {
    const response = await axios.post(`/courses/${courseId.value}/questions`, questionForm)
    
    if (response.data.success) {
      ElMessage.success('问题添加成功')
      addQuestionDialogVisible.value = false
      await fetchQuestions()
    } else {
      ElMessage.error(response.data.message || '添加问题失败')
    }
  } catch (error) {
    console.error('添加问题失败', error)
    ElMessage.error('添加问题失败')
  } finally {
    submitting.value = false
  }
}

// 查看问题详情
const viewQuestion = (question) => {
  currentQuestion.value = question
  // 初始化编辑表单数据
  editQuestionForm.content = question.content
  editQuestionForm.reference_answer = question.reference_answer
  isEditingQuestion.value = false
  viewQuestionDialogVisible.value = true
}

// 开始编辑问题
const startEditQuestion = () => {
  isEditingQuestion.value = true
}

// 取消编辑问题
const cancelEditQuestion = () => {
  // 恢复原始数据
  if (currentQuestion.value) {
    editQuestionForm.content = currentQuestion.value.content
    editQuestionForm.reference_answer = currentQuestion.value.reference_answer
  }
  isEditingQuestion.value = false
}

// 保存编辑的问题
const saveQuestion = async () => {
  if (!currentQuestion.value) return
  
  if (!editQuestionForm.content || !editQuestionForm.reference_answer) {
    ElMessage.warning('请填写完整问题和参考答案')
    return
  }
  
  submitting.value = true
  
  try {
    const response = await axios.put(`/api/questions/${currentQuestion.value.id}`, {
      content: editQuestionForm.content,
      reference_answer: editQuestionForm.reference_answer
    })
    
    if (response.data.success) {
      ElMessage.success('问题更新成功')
      // 更新本地数据
      currentQuestion.value.content = editQuestionForm.content
      currentQuestion.value.reference_answer = editQuestionForm.reference_answer
      
      // 更新问题列表中的数据
      const index = questions.value.findIndex(q => q.id === currentQuestion.value.id)
      if (index !== -1) {
        questions.value[index].content = editQuestionForm.content
        questions.value[index].reference_answer = editQuestionForm.reference_answer
      }
      
      isEditingQuestion.value = false
      viewQuestionDialogVisible.value = false
      await fetchQuestions()
    } else {
      ElMessage.error(response.data.message || '更新问题失败')
    }
  } catch (error) {
    console.error('更新问题失败', error)
    ElMessage.error('更新问题失败')
  } finally {
    submitting.value = false
  }
}

// 删除问题
const confirmDeleteQuestion = (question) => {
  ElMessageBox.confirm(`确定要删除这个问题吗？此操作不可恢复。`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await axios.delete(`/questions/${question.id}`)
      if (response.data.success) {
        ElMessage.success('问题已删除')
        await fetchQuestions()
      } else {
        ElMessage.error(response.data.message || '删除问题失败')
      }
    } catch (error) {
      console.error('删除问题失败', error)
      ElMessage.error('删除问题失败')
    }
  }).catch(() => {})
}

onMounted(async () => {
  await fetchCourse()
  await Promise.all([
    fetchKnowledgeGraph(),
    fetchQuestions(),
    fetchStudentAnswers()
  ])
})
</script>

<style scoped>
.course-detail {
  padding: 20px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.course-title h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
}

.course-meta-tags {
  display: flex;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.course-content {
  display: flex;
  gap: 25px;
}

.course-sidebar {
  width: 250px;
  flex-shrink: 0;
  background-color: #f9f9f9;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  height: fit-content;
}

.course-image {
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.course-image img:hover {
  transform: scale(1.05);
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 40px;
  border-radius: 8px;
}

.course-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-actions .el-button {
  width: 100%;
}

.course-main {
  flex: 1;
}

.course-description {
  margin-bottom: 25px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.course-description h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 10px;
}

.knowledge-graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 10px;
}

.knowledge-graph-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.view-toggle {
  display: flex;
  gap: 10px;
}

.knowledge-graph-container {
  height: 500px;
  border: 1px solid #EBEEF5;
  border-radius: 10px;
  padding: 5px;
  background-color: #ffffff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 25px;
}

.knowledge-list-container {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.questions-management {
  margin-bottom: 25px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 10px;
}

.questions-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.student-answers {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.student-answers h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 10px;
}

.answer-details {
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.question-section, .answer-section, .feedback-section {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #eaeaea;
}

.question-section:last-child, .answer-section:last-child, .feedback-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.question-section h4, .answer-section h4, .feedback-section h4 {
  margin: 0 0 8px 0;
  color: #409EFF;
  font-size: 15px;
}

.question-section p, .answer-section p, .feedback-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.course-tabs {
  margin-top: 20px;
}

.course-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  height: 50px;
  line-height: 50px;
}

.course-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
}

.course-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 2px;
}

.avatar-uploader {
  width: 178px;
  height: 178px;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
  border-radius: 8px;
}

.question-detail {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.question-detail h3 {
  margin-top: 0;
  color: #303133;
  font-size: 18px;
  margin-bottom: 15px;
  border-bottom: 2px solid #e6e6e6;
  padding-bottom: 10px;
}

.question-detail p {
  margin: 0 0 20px 0;
  color: #606266;
  line-height: 1.6;
  padding: 10px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.question-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #e6e6e6;
}

.question-detail :deep(.el-textarea__inner) {
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 10px;
  transition: all 0.3s ease;
}

.question-detail :deep(.el-textarea__inner:focus) {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.question-detail :deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}
</style> 