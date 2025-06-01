<template>
  <app-layout>
    <div class="course-detail" v-loading="loading">
      <!-- 动态背景装饰 -->
      <div class="background-decoration"></div>
      
      <template v-if="course">
        <div class="course-header animate__animated animate__fadeInDown">
          <div class="course-title">
            <h2 class="title-gradient">{{ course.title }}</h2>
            <div class="course-meta-tags">
              <el-tag>{{ course.teachers?.join(', ') }}</el-tag>
              <el-tag type="success">学生: {{ course.students_count }}</el-tag>
              <el-tag type="warning">问题: {{ course.questions_count }}</el-tag>
            </div>
          </div>
          <div class="header-actions">
            <el-button @click="router.push('/course-management')" class="back-btn">返回</el-button>
            <el-button type="primary" @click="showEditCourseDialog" class="edit-btn">编辑课程</el-button>
          </div>
        </div>
        
        <div class="course-content">
          <div class="course-sidebar animate__animated animate__fadeInLeft">
            <div class="course-image">
              <img v-if="course.image_path" :src="getImageUrl(course.image_path)" alt="课程图片" />
              <div v-else class="no-image">
                <el-icon><el-icon-picture /></el-icon>
              </div>
            </div>
            
            <div class="course-actions">
              <el-button v-if="course.file_path" type="success" icon="el-icon-download" @click="downloadFile" class="download-btn">
                下载课程文件
              </el-button>
              
              <el-button type="danger" icon="el-icon-delete" @click="confirmDeleteCourse" class="delete-btn">
                删除课程
              </el-button>
            </div>
          </div>
          
          <div class="course-main animate__animated animate__fadeInRight">
            <div class="course-description">
              <h3 class="section-title">课程描述</h3>
              <p>{{ course.description || '暂无描述' }}</p>
            </div>
            
            <el-tabs class="course-tabs">
              <el-tab-pane label="知识图谱">
                <div class="knowledge-graph-header">
                  <h3 class="section-title">课程知识结构</h3>
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
                    <h3 class="section-title">课程问题 ({{ questions.length }})</h3>
                    <el-button type="primary" size="small" @click="showAddQuestionDialog" class="add-question-btn">
                      添加问题
                    </el-button>
                  </div>
                  
                  <el-table v-if="questions.length > 0" :data="questions" border style="width: 100%" class="fancy-table">
                    <el-table-column prop="id" label="ID" width="60"></el-table-column>
                    <el-table-column prop="content" label="问题内容" show-overflow-tooltip></el-table-column>
                    <el-table-column label="操作" width="150">
                      <template #default="scope">
                        <div class="table-actions">
                          <el-button size="small" @click="viewQuestion(scope.row)" class="view-btn">查看</el-button>
                          <el-button size="small" type="danger" @click="confirmDeleteQuestion(scope.row)" class="delete-btn">删除</el-button>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table>
                  <el-empty v-else description="暂无问题"></el-empty>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="学生答题">
                <div class="student-answers">
                  <h3 class="section-title">学生答题情况</h3>
                  
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
      <el-dialog v-model="editDialogVisible" title="编辑课程" width="600px" class="fancy-dialog">
        // ... existing code ...
      </el-dialog>
      
      <!-- 添加问题对话框 -->
      <el-dialog v-model="addQuestionDialogVisible" title="添加问题" width="600px" class="fancy-dialog">
        // ... existing code ...
      </el-dialog>
      
      <!-- 查看问题对话框 -->
      <el-dialog v-model="viewQuestionDialogVisible" title="问题详情" width="600px" class="fancy-dialog">
        // ... existing code ...
      </el-dialog>
    </div>
  </app-layout>
</template>

<script setup>
// ... existing code ...
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.course-detail {
  padding: 20px;
  position: relative;
  min-height: calc(100vh - 100px);
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  overflow: hidden;
}

/* 动态背景效果 - 类似CourseList.vue */
.course-detail::before {
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
.course-detail::after {
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

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.course-header:hover {
  box-shadow: 0 8px 25px rgba(94, 114, 235, 0.12);
  transform: translateY(-2px);
}

.title-gradient {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
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

.course-header:hover .title-gradient::after {
  width: 80px;
}

.course-meta-tags {
  display: flex;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.back-btn, .edit-btn {
  transition: all 0.3s ease;
}

.back-btn:hover, .edit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.edit-btn {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border: none;
}

.course-content {
  display: flex;
  gap: 25px;
  position: relative;
  z-index: 1;
}

.course-sidebar {
  width: 250px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  height: fit-content;
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.course-sidebar:hover {
  box-shadow: 0 8px 25px rgba(94, 114, 235, 0.12);
  transform: translateY(-2px);
}

.course-image {
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  position: relative;
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

.course-image:hover::after {
  opacity: 1;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.course-image:hover img {
  transform: scale(1.08);
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
  border-radius: 8px;
  transition: all 0.3s ease;
}

.course-image:hover .no-image {
  transform: scale(1.05);
}

.course-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.download-btn, .delete-btn {
  width: 100%;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.download-btn {
  background: linear-gradient(45deg, #10b981, #059669);
  border: none;
}

.delete-btn {
  background: linear-gradient(45deg, #ef4444, #dc2626);
  border: none;
}

.download-btn:hover, .delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.course-main {
  flex: 1;
}

.course-description, .knowledge-list-container, .questions-management, .student-answers {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.course-description:hover, .knowledge-list-container:hover, .questions-management:hover, .student-answers:hover {
  box-shadow: 0 8px 25px rgba(94, 114, 235, 0.12);
  transform: translateY(-2px);
}

.section-title {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
  position: relative;
  padding-bottom: 10px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 2px;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.section-title:hover::after {
  width: 100px;
}

.knowledge-graph-container {
  height: 500px;
  border: 1px solid rgba(235, 238, 245, 0.5);
  border-radius: 10px;
  padding: 5px;
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 25px;
  overflow: hidden;
}

.knowledge-graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(230, 230, 230, 0.5);
}

.questions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(230, 230, 230, 0.5);
}

.add-question-btn {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border: none;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.add-question-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(94, 114, 235, 0.2);
}

.table-actions {
  display: flex;
  gap: 8px;
}

.view-btn {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.view-btn:hover, .delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.answer-details {
  padding: 15px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.answer-details:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.question-section, .answer-section, .feedback-section {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed rgba(234, 234, 234, 0.7);
}

.question-section:last-child, .answer-section:last-child, .feedback-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.question-section h4, .answer-section h4, .feedback-section h4 {
  margin: 0 0 8px 0;
  color: #5e72eb;
  font-size: 15px;
}

.question-section p, .answer-section p, .feedback-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  background: rgba(255, 255, 255, 0.7);
  padding: 10px;
  border-radius: 8px;
  border: 1px solid rgba(235, 238, 245, 0.5);
  transition: all 0.3s ease;
}

.question-section p:hover, .answer-section p:hover, .feedback-section p:hover {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.course-tabs {
  margin-top: 20px;
}

.course-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  height: 50px;
  line-height: 50px;
  transition: all 0.3s ease;
}

.course-tabs :deep(.el-tabs__item:hover) {
  color: #5e72eb;
  transform: translateY(-2px);
}

.course-tabs :deep(.el-tabs__item.is-active) {
  color: #5e72eb;
}

.course-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
}

.course-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 2px;
  background-color: rgba(230, 230, 230, 0.5);
}

/* 美化对话框 */
.fancy-dialog :deep(.el-dialog__header) {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  padding: 15px 20px;
}

.fancy-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.fancy-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.fancy-dialog :deep(.el-dialog__body) {
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
  position: relative;
  overflow: hidden;
}

.fancy-dialog :deep(.el-dialog__body)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 10% 10%, rgba(94, 114, 235, 0.05), transparent 30%),
    radial-gradient(circle at 90% 30%, rgba(0, 210, 255, 0.05), transparent 40%);
  z-index: 0;
  pointer-events: none;
}

/* 美化表格 */
.fancy-table {
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.fancy-table :deep(th) {
  background-color: rgba(248, 250, 252, 0.8) !important;
  color: #334155;
  font-weight: 600;
  padding: 15px 12px;
  transition: all 0.3s ease;
}

.fancy-table :deep(tr) {
  transition: all 0.3s ease;
}

.fancy-table :deep(tr:hover) {
  background-color: rgba(248, 249, 254, 0.9) !important;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 2;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .course-header, .course-content {
    flex-direction: column;
  }
  
  .course-sidebar {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .header-actions {
    margin-top: 15px;
  }
  
  .table-actions {
    flex-direction: column;
    gap: 5px;
  }
}
</style> 