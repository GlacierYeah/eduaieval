<template>
  <app-layout>
    <div class="course-management">
      <div class="page-header">
        <h2>课程管理</h2>
        <el-button type="primary" @click="showAddCourseDialog">新增课程</el-button>
      </div>
      
      <el-table v-loading="loading" :data="courses" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column label="课程封面" width="120">
          <template #default="scope">
            <el-image 
              v-if="scope.row.image_path" 
              :src="getImageUrl(scope.row.image_path)" 
              fit="cover"
              style="width: 100px; height: 60px;"
            ></el-image>
            <div v-else class="no-image">无图片</div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="课程名称"></el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip></el-table-column>
        <el-table-column prop="students_count" label="学生数量" width="100"></el-table-column>
        <el-table-column prop="questions_count" label="问题数量" width="100"></el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" @click="viewCourse(scope.row)">查看</el-button>
            <el-button size="small" type="danger" @click="deleteCourse(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 新增课程对话框 -->
      <el-dialog v-model="dialogVisible" title="新增课程" width="600px">
        <el-form :model="courseForm" :rules="rules" ref="courseFormRef" label-width="100px">
          <el-form-item label="课程名称" prop="title">
            <el-input v-model="courseForm.title"></el-input>
          </el-form-item>
          <el-form-item label="课程描述" prop="description">
            <el-input type="textarea" v-model="courseForm.description" rows="4"></el-input>
          </el-form-item>
          <el-form-item label="课程封面">
            <el-upload
              class="avatar-uploader"
              action="#"
              :auto-upload="false"
              :on-change="handleImageChange"
              :show-file-list="false"
            >
              <img v-if="imageUrl" :src="imageUrl" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><el-icon-plus /></el-icon>
            </el-upload>
            <div class="upload-tip">点击上传课程封面图片</div>
          </el-form-item>
          <el-form-item label="课程文件" prop="file">
            <el-upload
              class="file-uploader"
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
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="submitLoading" @click="submitCourse">提交</el-button>
          </div>
        </template>
      </el-dialog>
      
      <!-- 学生管理对话框 -->
      <el-dialog v-model="studentDialogVisible" :title="currentCourse?.title + ' - 学生管理'" width="600px">
        <div v-if="currentCourse" class="student-management">
          <div class="add-student-section">
            <h4>添加学生</h4>
            <el-select v-model="selectedStudent" filterable placeholder="选择学生">
              <el-option
                v-for="student in availableStudents"
                :key="student.id"
                :label="student.username"
                :value="student.id"
              ></el-option>
            </el-select>
            <el-button type="primary" :disabled="!selectedStudent" @click="addStudentToCourse">添加</el-button>
          </div>
          
          <h4>已加入的学生</h4>
          <el-table :data="courseStudents" style="width: 100%" v-loading="studentsLoading">
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="username" label="用户名"></el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button size="small" type="danger" @click="removeStudentFromCourse(scope.row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-dialog>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'
import AppLayout from '../../components/AppLayout.vue'

// 状态变量
const router = useRouter()
const courses = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const studentDialogVisible = ref(false)
const submitLoading = ref(false)
const imageUrl = ref('')
const currentCourse = ref(null)
const courseStudents = ref([])
const availableStudents = ref([])
const selectedStudent = ref(null)
const studentsLoading = ref(false)

// 表单相关
const courseFormRef = ref(null)
const courseForm = reactive({
  title: '',
  description: '',
  image: null,
  file: null
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入课程描述', trigger: 'blur' }
  ],
  file: [
    { required: true, message: '请上传课程文件', trigger: 'change' }
  ]
}

// 生命周期钩子
onMounted(() => {
  fetchCourses()
})

// 获取课程列表
const fetchCourses = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/courses')
    courses.value = response.data.courses
  } catch (error) {
    console.error('获取课程列表失败', error)
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  return `http://localhost:5000/static/uploads/${path}`
}

// 查看课程详情
const viewCourse = (course) => {
  router.push(`/course-detail/${course.id}`)
}

// 删除课程
const deleteCourse = (course) => {
  ElMessageBox.confirm(`确定要删除课程 "${course.title}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/courses/${course.id}`)
      ElMessage.success('删除成功')
      fetchCourses()
    } catch (error) {
      console.error('删除课程失败', error)
      ElMessage.error('删除课程失败')
    }
  }).catch(() => {})
}

// 显示添加课程对话框
const showAddCourseDialog = () => {
  dialogVisible.value = true
  // 重置表单
  if (courseFormRef.value) {
    courseFormRef.value.resetFields()
  }
  courseForm.title = ''
  courseForm.description = ''
  courseForm.image = null
  courseForm.file = null
  imageUrl.value = ''
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
  
  courseForm.image = file.raw
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
  
  courseForm.file = file.raw
}

// 提交课程表单
const submitCourse = async () => {
  if (!courseFormRef.value) return
  
  try {
    await courseFormRef.value.validate()
    
    if (!courseForm.file) {
      ElMessage.error('请上传课程文件')
      return
    }
    
    submitLoading.value = true
    
    // 使用FormData提交表单数据
    const formData = new FormData()
    formData.append('title', courseForm.title)
    formData.append('description', courseForm.description)
    
    if (courseForm.image) {
      formData.append('image', courseForm.image)
    }
    
    if (courseForm.file) {
      formData.append('file', courseForm.file)
    }
    
    // 提交表单
    const response = await axios.post('/api/courses', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      ElMessage.success('课程创建成功')
      dialogVisible.value = false
      fetchCourses()
    } else {
      ElMessage.error(response.data.message || '课程创建失败')
    }
  } catch (error) {
    console.error('提交课程失败', error)
    ElMessage.error(error.response?.data?.message || '课程创建失败')
  } finally {
    submitLoading.value = false
  }
}

// 管理课程学生
const manageCourseStudents = async (course) => {
  currentCourse.value = course
  studentDialogVisible.value = true
  studentsLoading.value = true
  
  try {
    // 获取该课程的学生
    const courseStudentsResponse = await axios.get(`/courses/${course.id}/students`)
    courseStudents.value = courseStudentsResponse.data.students || []
    
    // 获取所有学生
    const allStudentsResponse = await axios.get('/students')
    const allStudents = allStudentsResponse.data.students || []
    
    // 过滤出未加入课程的学生
    availableStudents.value = allStudents.filter(student => 
      !courseStudents.value.some(s => s.id === student.id)
    )
  } catch (error) {
    console.error('获取学生数据失败', error)
    ElMessage.error('获取学生数据失败')
  } finally {
    studentsLoading.value = false
  }
}

// 添加学生到课程
const addStudentToCourse = async () => {
  if (!currentCourse.value || !selectedStudent.value) return
  
  try {
    await axios.post(`/courses/${currentCourse.value.id}/students`, {
      student_id: selectedStudent.value
    })
    
    ElMessage.success('添加学生成功')
    // 刷新学生列表
    manageCourseStudents(currentCourse.value)
  } catch (error) {
    console.error('添加学生失败', error)
    ElMessage.error(error.response?.data?.message || '添加学生失败')
  }
}

// 从课程中移除学生
const removeStudentFromCourse = async (student) => {
  if (!currentCourse.value) return
  
  ElMessageBox.confirm(`确定要将学生 "${student.username}" 从课程中移除吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/courses/${currentCourse.value.id}/students/${student.id}`)
      ElMessage.success('移除学生成功')
      // 刷新学生列表
      manageCourseStudents(currentCourse.value)
    } catch (error) {
      console.error('移除学生失败', error)
      ElMessage.error('移除学生失败')
    }
  }).catch(() => {})
}
</script>

<style scoped>
.course-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.no-image {
  width: 100px;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 12px;
}

.avatar-uploader {
  width: 178px;
  height: 178px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
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
}

.upload-tip {
  font-size: 12px;
  color: #606266;
  margin-top: 7px;
}

.student-management {
  padding: 10px 0;
}

.add-student-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.add-student-section h4 {
  margin: 0;
  margin-right: 10px;
}
</style> 