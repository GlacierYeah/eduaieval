<template>
  <app-layout>
    <div class="home-page">
      <!-- 动态背景元素 -->
      <div class="animated-background">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
      
      <!-- 顶部横幅 -->
      <div class="hero-section animate__animated animate__fadeIn">
        <div class="hero-content animate__animated animate__slideInLeft animate__delay-1s">
          <div class="badge">智能教育平台</div>
          <h1 class="hero-title">
            <span class="highlight">AI</span> 赋能教育<br>开启智慧学习新时代
          </h1>
          <p class="hero-subtitle">根据您的角色，我们为您定制了最适合的学习和教学工具</p>
          <div class="hero-actions">
            <div class="hero-stat">
              <div class="stat-number counter">5000+</div>
              <div class="stat-label">学生使用</div>
            </div>
            <div class="hero-stat">
              <div class="stat-number counter">200+</div>
              <div class="stat-label">精品课程</div>
            </div>
            <div class="hero-stat">
              <div class="stat-number counter">98%</div>
              <div class="stat-label">满意度</div>
            </div>
          </div>
        </div>
        <div class="hero-image animate__animated animate__slideInRight animate__delay-1s">
          <div class="image-container">
            <img src="../assets/education-hero.svg" alt="AI教育" />
            <div class="image-decoration"></div>
          </div>
        </div>
      </div>
      
      <!-- 功能卡片部分 -->
      <div class="features-section">
        <h2 class="section-title animate__animated animate__fadeIn">核心功能</h2>
        <p class="section-subtitle animate__animated animate__fadeIn animate__delay-1s">为您提供全方位的教育解决方案</p>
        
        <div class="features-grid">
          <!-- 教师功能卡片 -->
          <template v-if="userStore.isTeacher">
            <div class="feature-card animate__animated animate__fadeInUp" 
                 @click="router.push('/course-management')"
                 style="--delay: 0.1s">
              <div class="feature-icon-wrapper purple">
                <i class="feature-icon fas fa-book"></i>
              </div>
              <h3 class="feature-title">课程管理</h3>
              <p class="feature-desc">创建、编辑和管理您的课程内容，轻松构建知识体系</p>
              <el-button text class="feature-link">
                进入管理 <el-icon><el-icon-arrow-right /></el-icon>
              </el-button>
              <div class="card-shine"></div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" 
                 @click="router.push('/student-management')"
                 style="--delay: 0.2s">
              <div class="feature-icon-wrapper green">
                <i class="feature-icon fas fa-users"></i>
              </div>
              <h3 class="feature-title">学生管理</h3>
              <p class="feature-desc">查看和管理学生信息及学习进度，实时掌握教学效果</p>
              <el-button text class="feature-link">
                管理学生 <el-icon><el-icon-arrow-right /></el-icon>
              </el-button>
              <div class="card-shine"></div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" 
                 @click="router.push('/data-statistics')"
                 style="--delay: 0.3s">
              <div class="feature-icon-wrapper blue">
                <i class="feature-icon fas fa-chart-bar"></i>
              </div>
              <h3 class="feature-title">数据统计</h3>
              <p class="feature-desc">分析学生学习数据和课程效果，优化教学策略</p>
              <el-button text class="feature-link">
                查看报表 <el-icon><el-icon-arrow-right /></el-icon>
              </el-button>
              <div class="card-shine"></div>
            </div>
          </template>
          
          <!-- 学生功能卡片 -->
          <template v-if="userStore.isStudent">
            <div class="feature-card animate__animated animate__fadeInUp" 
                 @click="router.push('/courses')"
                 style="--delay: 0.1s">
              <div class="feature-icon-wrapper blue">
                <i class="feature-icon fas fa-graduation-cap"></i>
              </div>
              <h3 class="feature-title">课程列表</h3>
              <p class="feature-desc">浏览和学习您的课程内容，随时随地开启学习之旅</p>
              <el-button text class="feature-link">
                开始学习 <el-icon><el-icon-arrow-right /></el-icon>
              </el-button>
              <div class="card-shine"></div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" 
                 @click="router.push('/chat-history')"
                 style="--delay: 0.2s">
              <div class="feature-icon-wrapper purple">
                <i class="feature-icon fas fa-comments"></i>
              </div>
              <h3 class="feature-title">对话记录</h3>
              <p class="feature-desc">查看与AI助手的交流历史记录，回顾学习要点</p>
              <el-button text class="feature-link">
                查看记录 <el-icon><el-icon-arrow-right /></el-icon>
              </el-button>
              <div class="card-shine"></div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" 
                 @click="router.push('/level-analysis')"
                 style="--delay: 0.3s">
              <div class="feature-icon-wrapper green">
                <i class="feature-icon fas fa-chart-line"></i>
              </div>
              <h3 class="feature-title">等级分析</h3>
              <p class="feature-desc">查看您的学习水平和进步情况，发现学习规律</p>
              <el-button text class="feature-link">
                查看分析 <el-icon><el-icon-arrow-right /></el-icon>
              </el-button>
              <div class="card-shine"></div>
            </div>
          </template>
        </div>
      </div>
      
      <!-- 平台优势部分 -->
      <div class="advantages-section animate__animated animate__fadeIn" data-scroll>
        <h2 class="section-title">平台优势</h2>
        <p class="section-subtitle">智能化学习体验，个性化教育解决方案</p>
        
        <div class="advantages-grid">
          <div class="advantage-item" data-scroll>
            <div class="advantage-icon">
              <i class="fas fa-brain"></i>
            </div>
            <h3>AI驱动学习</h3>
            <p>利用人工智能技术分析学习行为，推荐最适合的学习内容</p>
          </div>
          
          <div class="advantage-item" data-scroll>
            <div class="advantage-icon">
              <i class="fas fa-puzzle-piece"></i>
            </div>
            <h3>个性化学习路径</h3>
            <p>根据学习能力和进度，定制专属学习计划</p>
          </div>
          
          <div class="advantage-item" data-scroll>
            <div class="advantage-icon">
              <i class="fas fa-robot"></i>
            </div>
            <h3>数字人在线问答</h3>
            <p>智能数字人助手提供24小时实时解答，让学习过程更加高效互动</p>
          </div>
          
          <div class="advantage-item" data-scroll>
            <div class="advantage-icon">
              <i class="fas fa-chart-pie"></i>
            </div>
            <h3>数据可视化</h3>
            <p>直观展示学习进度和成果，激发学习动力</p>
          </div>
          
          <div class="advantage-item" data-scroll>
            <div class="advantage-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <h3>安全可靠</h3>
            <p>严格保护用户数据隐私，提供安全的学习环境</p>
          </div>
        </div>
      </div>
      
      <!-- 底部波浪装饰 -->
      <div class="wave-container">
        <div class="wave wave1"></div>
        <div class="wave wave2"></div>
        <div class="wave wave3"></div>
      </div>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'

const userStore = useUserStore()
const router = useRouter()

// 格式化日期
const formatDate = (date) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return new Intl.DateTimeFormat('zh-CN', options).format(date)
}

// 数字动画效果
const animateCounters = () => {
  const counters = document.querySelectorAll('.counter')
  
  counters.forEach(counter => {
    const target = parseInt(counter.innerText.replace(/\D/g, ''), 10)
    let count = 0
    const duration = 2000 // 动画持续时间（毫秒）
    const increment = Math.ceil(target / (duration / 16)) // 每帧增加的数量
    
    const updateCount = () => {
      count += increment
      
      if (count >= target) {
        counter.innerText = counter.innerText.includes('+') ? 
          target + '+' : counter.innerText.includes('%') ?
          target + '%' : target
        return
      }
      
      counter.innerText = counter.innerText.includes('+') ? 
        count + '+' : counter.innerText.includes('%') ?
        count + '%' : count
      
      requestAnimationFrame(updateCount)
    }
    
    updateCount()
  })
}

// 滚动动画
const initScrollAnimation = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-visible')
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1 })

  // 监听所有带有data-scroll属性的元素
  document.querySelectorAll('[data-scroll]').forEach(el => {
    observer.observe(el)
  })
}

onMounted(() => {
  // 加载动画库
  const animateCSSLink = document.createElement('link')
  animateCSSLink.rel = 'stylesheet'
  animateCSSLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
  document.head.appendChild(animateCSSLink)
  
  // 加载Font Awesome图标
  const fontAwesomeLink = document.createElement('link')
  fontAwesomeLink.rel = 'stylesheet'
  fontAwesomeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
  document.head.appendChild(fontAwesomeLink)
  
  // 初始化数字动画
  setTimeout(() => {
    animateCounters()
  }, 1000)
  
  // 初始化滚动动画
  initScrollAnimation()
})
</script>

<style scoped>
/* 新的色彩方案 */
:root {
  --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --secondary-gradient: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  --accent-purple: #8b5cf6;
  --accent-blue: #3b82f6;
  --accent-green: #10b981;
  --accent-pink: #ec4899;
  --bg-gradient: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  --text-dark: #1f2937;
  --text-medium: #4b5563;
  --text-light: #9ca3af;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* 引入动画库 */
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

.home-page {
  padding-bottom: 40px;
  position: relative;
  overflow: hidden;
  background: var(--bg-gradient);
}

/* 动态背景元素 */
.animated-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  opacity: 0.7;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
}

.shape-1 {
  top: -100px;
  right: -100px;
  width: 400px;
  height: 400px;
  background: rgba(99, 102, 241, 0.1);
  animation: float 20s infinite alternate ease-in-out;
}

.shape-2 {
  bottom: -150px;
  left: -150px;
  width: 600px;
  height: 600px;
  background: rgba(16, 185, 129, 0.1);
  animation: float 25s infinite alternate-reverse ease-in-out;
}

.shape-3 {
  top: 40%;
  left: 25%;
  width: 300px;
  height: 300px;
  background: rgba(236, 72, 153, 0.1);
  animation: pulse 15s infinite alternate ease-in-out;
}

.shape-4 {
  top: 60%;
  right: 20%;
  width: 250px;
  height: 250px;
  background: rgba(59, 130, 246, 0.1);
  animation: pulse 18s infinite alternate-reverse ease-in-out;
}

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(30px, -30px) rotate(5deg); }
  100% { transform: translate(-30px, 30px) rotate(-5deg); }
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
  100% { transform: scale(0.8); opacity: 0.5; }
}

/* 英雄区域样式 */
.hero-section {
  display: flex;
  align-items: center;
  padding: 80px 0;
  margin-bottom: 80px;
  position: relative;
  z-index: 1;
}

.hero-content {
  flex: 1;
  padding: 0 60px;
  position: relative;
  z-index: 1;
}

.badge {
  display: inline-block;
  padding: 8px 16px;
  background: var(--primary-gradient);
  color: white;
  border-radius: 30px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  animation: pulse 2s infinite;
}

.hero-title {
  font-size: 3.5rem;
  line-height: 1.2;
  margin-bottom: 24px;
  color: var(--text-dark);
  font-weight: 800;
  letter-spacing: -0.02em;
}

.highlight {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
  display: inline-block;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 5px;
  left: 0;
  width: 100%;
  height: 8px;
  background-color: rgba(139, 92, 246, 0.3);
  z-index: -1;
  border-radius: 4px;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-medium);
  margin-bottom: 40px;
  max-width: 500px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 30px;
}

.hero-stat {
  display: flex;
  flex-direction: column;
  gap: 5px;
  animation: fadeInUp 1s forwards;
  animation-delay: calc(var(--delay, 0) * 1s);
  opacity: 0;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--accent-purple);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-medium);
  font-weight: 500;
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 1;
}

.image-container {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.hero-image img {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 20px 30px rgba(0, 0, 0, 0.15));
  animation: float 6s ease-in-out infinite;
  position: relative;
  z-index: 2;
}

.image-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--primary-gradient);
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  filter: blur(40px);
  opacity: 0.3;
  animation: morphing 15s infinite;
  z-index: 1;
}

@keyframes morphing {
  0% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; }
  25% { border-radius: 50% 50% 50% 50% / 50% 50% 50% 50%; }
  50% { border-radius: 70% 30% 30% 70% / 70% 70% 30% 30%; }
  75% { border-radius: 40% 60% 60% 40% / 60% 40% 60% 40%; }
  100% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; }
}

/* 功能区域样式 */
.features-section {
  margin-bottom: 80px;
  position: relative;
  z-index: 1;
  padding: 0 20px;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  color: var(--text-dark);
  margin-bottom: 16px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.section-subtitle {
  text-align: center;
  color: var(--text-medium);
  margin-bottom: 60px;
  font-size: 1.125rem;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 30px;
}

.feature-card {
  background-color: white;
  border-radius: 24px;
  padding: 36px;
  box-shadow: var(--shadow-lg);
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(0, 0, 0, 0.03);
  height: 100%;
  position: relative;
  overflow: hidden;
  animation-delay: var(--delay);
  transform: translateY(20px);
  opacity: 0;
  animation-fill-mode: forwards;
}

.feature-card::before {
  content: '';
  position: absolute;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: rgba(139, 92, 246, 0.05);
  top: -30px;
  right: -30px;
  transition: all 0.5s ease;
  z-index: 0;
}

.feature-card:hover {
  transform: translateY(-15px) scale(1.03);
  box-shadow: var(--shadow-xl);
}

.feature-card:hover::before {
  transform: scale(1.8);
}

.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.2) 50%,
    transparent 100%
  );
  transition: left 0.7s ease;
  pointer-events: none;
  z-index: 2;
}

.feature-card:hover .card-shine {
  left: 100%;
}

.feature-icon-wrapper {
  width: 70px;
  height: 70px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.5s ease;
  position: relative;
  z-index: 1;
}

.feature-card:hover .feature-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.feature-icon-wrapper.blue {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.feature-icon-wrapper.green {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.feature-icon-wrapper.purple {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
}

.feature-icon {
  font-size: 28px;
  color: white;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--text-dark);
  position: relative;
  z-index: 1;
}

.feature-desc {
  color: var(--text-medium);
  margin-bottom: 24px;
  line-height: 1.7;
  flex-grow: 1;
  position: relative;
  z-index: 1;
}

.feature-link {
  color: var(--accent-purple);
  display: flex;
  align-items: center;
  padding: 0;
  margin-top: auto;
  font-size: 1rem;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.feature-link .el-icon {
  margin-left: 8px;
  transition: transform 0.3s;
}

.feature-link:hover .el-icon {
  transform: translateX(8px);
}

/* 平台优势部分 */
.advantages-section {
  margin-bottom: 100px;
  padding: 60px 20px;
  background: white;
  border-radius: 30px;
  box-shadow: var(--shadow-lg);
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}

.advantages-section.animate-visible {
  opacity: 1;
  transform: translateY(0);
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-top: 50px;
}

.advantage-item {
  text-align: center;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease;
  transition-delay: calc(var(--index, 0) * 0.1s);
}

.advantage-item.animate-visible {
  opacity: 1;
  transform: translateY(0);
}

.advantage-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: white;
  font-size: 32px;
  box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
  transition: all 0.3s ease;
}

.advantage-item:hover .advantage-icon {
  transform: scale(1.1) translateY(-10px);
}

.advantage-item h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-dark);
}

.advantage-item p {
  color: var(--text-medium);
  line-height: 1.6;
}

/* 波浪装饰效果 */
.wave-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 150px;
  overflow: hidden;
  z-index: 0;
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200%;
  height: 100px;
  background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0 0v46.29c47.79 22.2 103.59 32.17 158 28 70.36-5.37 136.33-33.31 206.8-37.5 73.84-4.36 147.54 16.88 218.2 35.26 69.27 18 138.3 24.88 209.4 13.08 36.15-6 69.85-17.84 104.45-29.34C989.49 25 1113-14.29 1200 52.47V0z" opacity=".25" fill="white"/></svg>');
  background-size: 1200px 100px;
  animation: wave 25s linear infinite;
}

.wave1 {
  animation: wave 25s linear infinite;
  z-index: 3;
  opacity: 0.5;
}

.wave2 {
  animation: wave-reverse 20s linear infinite;
  bottom: 10px;
  opacity: 0.3;
  z-index: 2;
}

.wave3 {
  animation: wave 30s linear infinite;
  bottom: 15px;
  opacity: 0.2;
  z-index: 1;
}

@keyframes wave {
  0% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(-50%);
  }
  100% {
    transform: translateX(0);
  }
}

@keyframes wave-reverse {
  0% {
    transform: translateX(-50%);
  }
  50% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* 响应式样式 */
@media (max-width: 991px) {
  .hero-title {
    font-size: 2.8rem;
  }
  
  .hero-content {
    padding: 0 40px;
  }
  
  .section-title {
    font-size: 2.2rem;
  }
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
    padding: 60px 20px;
  }
  
  .hero-content {
    padding: 0 20px 40px;
  }
  
  .hero-title {
    font-size: 2.4rem;
  }
  
  .hero-subtitle {
    margin-left: auto;
    margin-right: auto;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .advantages-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
  
  .section-subtitle {
    font-size: 0.9rem;
  }
  
  .hero-actions {
    flex-wrap: wrap;
  }
}
</style> 