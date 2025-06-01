<template>
  <div class="course-management-container">
    <div class="wave-background"></div>
    <div class="content-wrapper">
      <h2 class="page-title">课程管理</h2>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-input
          v-model="searchInput"
          placeholder="请输入课程名称"
          class="search-input"
        >
          <template #append>
            <el-button @click="search" class="search-button">
              <i class="el-icon-search"></i> 搜索
            </el-button>
          </template>
        </el-input>
        <el-button type="primary" @click="showAddDialog" class="add-button">
          <i class="el-icon-plus"></i> 添加课程
        </el-button>
      </div>
      
      <!-- 课程表格 -->
      <div class="table-container">
        <el-table
          :data="displayCourses"
          border
          style="width: 100%"
          class="course-table"
          v-loading="tableLoading"
          element-loading-text="加载中..."
          element-loading-spinner="el-icon-loading"
          element-loading-background="rgba(255, 255, 255, 0.8)"
        >
        // ... existing code ...
        </el-table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[5, 10, 20, 50]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalItems"
          class="pagination"
        ></el-pagination>
      </div>
      
      <!-- 添加课程对话框 -->
      <el-dialog
        title="添加课程"
        v-model="dialogVisible"
        width="50%"
        class="custom-dialog"
      >
      // ... existing code ...
      </el-dialog>
      
      <!-- 修改课程对话框 -->
      <el-dialog
        title="修改课程信息"
        v-model="editDialogVisible"
        width="50%"
        class="custom-dialog"
      >
      // ... existing code ...
      </el-dialog>
    </div>
  </div>
</template>

<script>
// ... existing code ...
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.course-management-container {
  position: relative;
  min-height: 100vh;
  padding: 20px;
  overflow: hidden;
  animation: fadeIn 0.8s ease-in-out;
  background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 动态背景效果 - 类似CourseList.vue */
.course-management-container::before {
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
.course-management-container::after {
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

/* 浮动圆形装饰 */
.wave-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  opacity: 0.05;
  z-index: -1;
}

.wave-background:before,
.wave-background:after {
  content: "";
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  background: radial-gradient(ellipse at center, rgba(94, 114, 235, 0.3) 0%, rgba(255,255,255,0) 70%);
  animation: wave 15s linear infinite;
  z-index: -1;
}

.wave-background:after {
  animation-delay: -5s;
  animation-duration: 20s;
  opacity: 0.3;
  background: radial-gradient(ellipse at center, rgba(0, 210, 255, 0.3) 0%, rgba(255,255,255,0) 70%);
}

@keyframes wave {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.content-wrapper {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 15px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  padding: 25px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  animation: slideUp 0.6s ease-out;
  position: relative;
  z-index: 1;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-title {
  font-size: 28px;
  color: #4a5568;
  margin-bottom: 25px;
  position: relative;
  display: inline-block;
  font-weight: 700;
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: titleGlow 3s ease-in-out infinite alternate;
}

@keyframes titleGlow {
  0% {
    text-shadow: 0 0 5px rgba(94, 114, 235, 0.3);
  }
  100% {
    text-shadow: 0 0 15px rgba(0, 210, 255, 0.5);
  }
}

.search-area {
  display: flex;
  margin-bottom: 20px;
  gap: 15px;
  align-items: center;
}

.search-input {
  flex: 1;
  transition: all 0.3s ease;
}

.search-input:focus-within {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.search-button, .add-button {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.search-button:hover, .add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(94, 114, 235, 0.3);
}

.search-button:active, .add-button:active {
  transform: translateY(1px);
}

.add-button {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border: none;
}

.add-button:hover {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
}

.table-container {
  margin-bottom: 20px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.8s ease-in-out;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.course-table {
  border-radius: 10px;
  overflow: hidden;
}

.course-table ::v-deep(th) {
  background-color: rgba(248, 250, 252, 0.8) !important;
  color: #334155;
  font-weight: 600;
  padding: 15px 12px;
}

.course-table ::v-deep(td) {
  padding: 12px;
  transition: all 0.2s ease;
}

.course-table ::v-deep(.el-table__row) {
  transition: all 0.3s ease;
}

.course-table ::v-deep(.el-table__row:hover) {
  background-color: rgba(248, 249, 254, 0.9) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 25px;
}

.pagination {
  padding: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.custom-dialog {
  border-radius: 15px;
  overflow: hidden;
}

.custom-dialog ::v-deep(.el-dialog__header) {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  color: white;
  padding: 15px 20px;
}

.custom-dialog ::v-deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.custom-dialog ::v-deep(.el-dialog__body) {
  padding: 25px;
}

.custom-dialog ::v-deep(.el-form-item__label) {
  font-weight: 500;
  color: #4a5568;
}

.custom-dialog ::v-deep(.el-input__inner),
.custom-dialog ::v-deep(.el-textarea__inner) {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.custom-dialog ::v-deep(.el-input__inner:focus),
.custom-dialog ::v-deep(.el-textarea__inner:focus) {
  border-color: #a777e3;
  box-shadow: 0 0 0 2px rgba(167, 119, 227, 0.2);
}

.custom-dialog ::v-deep(.el-button) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.custom-dialog ::v-deep(.el-button--primary) {
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
  border: none;
}

.custom-dialog ::v-deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(94, 114, 235, 0.3);
  background: linear-gradient(45deg, #5e72eb, #00d2ff);
}

/* 负责任的响应式设计 */
@media screen and (max-width: 768px) {
  .search-area {
    flex-direction: column;
    align-items: stretch;
  }
  
  .content-wrapper {
    padding: 15px;
  }
  
  .custom-dialog {
    width: 90% !important;
  }
}
</style> 