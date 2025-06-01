<template>
  <app-layout>
    <div class="ai-assistant-page" v-loading="loading">
      <!-- 开始测试提示框 -->
      <el-dialog
        v-model="showStartDialog"
        title="开始AI测试"
        width="400px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :show-close="false"
      >
        <div class="start-dialog-content">
          <p>欢迎使用AI数字人助教系统，点击开始按钮进行测试。</p>
          <p>请确保您的设备开启了声音。</p>
        </div>
        <template #footer>
          <div class="dialog-footer">
            <!-- <el-button type="primary" @click="startTest" :loading="isVideoGenerationPending">
              {{ isVideoGenerationPending ? '正在准备视频...' : '开始测试' }}
            </el-button> -->
            <!-- 开始测试按钮 -->
            <el-button 
              v-if="!isVideoGenerationPending && !isTestStarting" 
              type="primary" 
              @click="startTest">
              开始测试
            </el-button>

            <!-- 正在准备视频按钮 -->
            <el-button 
              v-if="isVideoGenerationPending"
              type="primary" 
              :loading="isVideoGenerationPending" 
              :disabled="isVideoGenerationPending">
              正在准备视频...
            </el-button>
          </div>
        </template>
      </el-dialog>

      <el-card class="ai-container">
        <div class="page-header">
          <h2>AI数字人助教</h2>
          <div class="header-buttons">
            <el-button @click="logout" type="danger" plain>退出登录</el-button>
            <el-button @click="router.back()">返回</el-button>
          </div>
        </div>
        
        <div class="content-container">
          <!-- 数字人视频卡片 -->
          <div class="digital-human-section">
      <el-card class="digital-human-card">
        <div class="card-header">
          <h3>AI数字人</h3>
          <el-tag type="info">实时助教</el-tag>
        </div>
        <div class="video-container">
          <div class="video-wrapper">
            <video
              ref="videoPlayer"
              width="100%"
              height="auto"
              class="digital-human-video"
              
              @loadeddata="handleVideoLoaded"
              :src="currentVideoUrl"
              controls
            >
              您的浏览器不支持视频播放
            </video>
          </div>
        </div>
        <div class="video-controls-container">
          <el-button
            class="video-control-btn"
            type="primary"
            size="large"
            circle
            @click="toggleVideo"
          >
            <el-icon>
              <VideoPlay v-if="!isPlaying" />
              <VideoPause v-else />
            </el-icon>
          </el-button>
        </div>
        <div class="digital-human-info">
          <p>AI数字人助教将为您提供课程辅导与问题解答</p>
        </div>
      </el-card>
  </div>

          <!-- 答题区域 -->
          <div class="qa-section">
            <div class="course-info-header">
              <h3>{{ course && course.title || '加载中...' }}</h3>
              <div class="header-actions">
                <el-tag type="primary">当前题目: {{ currentQuestionIndex + 1 }}/{{ questions.length }}</el-tag>
                <el-button 
                  type="success" 
                  size="small" 
                  v-if="allQuestionsAnswered" 
                  :loading="pendingSubmit"
                  @click="submitAllAnswers"
                >
                  提交所有答案
                </el-button>
              </div>
            </div>

            <!-- 题目导航部分 -->
          <div class="question-navigation" v-if="questions.length > 0">
            <div class="question-buttons">
              <el-button 
                v-for="(question, index) in questions" 
                :key="question.id"
                :type="currentQuestionIndex === index ? 'primary' : 'default'"
                :class="{ 'answered': answeredQuestions.includes(question.id) }"
                @click="selectQuestion(index)"
                size="small"
              >
                题目 {{ index + 1 }}
              </el-button>
            </div>
          </div>
            
            <div class="question-container">
              <div v-if="currentQuestion" class="question-card">
                <h4>问题 {{ currentQuestionIndex + 1 }}：</h4>
                <p>{{ currentQuestion.content }}</p>
                
                <h4>您的回答：</h4>
                <div class="answer-input-container">
                  <el-input
                    v-model="userAnswer"
                    type="textarea"
                    rows="6"
                    placeholder="请输入您的答案..."
                    :disabled="isSubmitting || answeredQuestions.includes(currentQuestion.id)"
                  ></el-input>
                  
                  <!-- 语音输入按钮 -->
                  <div class="voice-input-controls" v-if="!answeredQuestions.includes(currentQuestion.id)">
                    <el-button 
                      :class="{ 'is-recording': isRecording }"
                      circle 
                      @click="toggleVoiceRecognition"
                      :title="isRecording ? '点击停止录音' : '点击开始语音输入'"
                      :disabled="isSubmitting"
                    >
                      <i class="voice-icon" :class="isRecording ? 'recording' : ''"></i>
                    </el-button>
                    <span v-if="isRecording" class="recording-text">正在录音...</span>
                  </div>
                </div>
                
                <div class="answer-actions">
                  <!-- 已回答的问题不显示操作按钮 -->
                  <template v-if="hasSubmitted">
                    <div class="answered-tag">
                      <el-tag type="success">已提交</el-tag>
                    </div>
                  </template>
                  <template v-else>
                    <el-button 
                      @click="saveCurrentAnswer" 
                      :disabled="isSubmitting || !userAnswer.trim()"
                    >
                      保存答案
                    </el-button>
                    <el-button 
                      type="primary" 
                      @click="moveToNextWithSave"
                      :disabled="!userAnswer.trim()"
                    >
                      保存并下一题
                    </el-button>
                    <el-button @click="skipQuestion" :disabled="isSubmitting">
                      跳过此题
                    </el-button>
                  </template>
                </div>
              </div>
              
              <div v-else-if="questions.length === 0 && !loading" class="no-questions">
                <el-empty description="该课程暂无问题"></el-empty>
              </div>
              
              <!-- 提交所有答案按钮 -->
              <div class="submit-all-section" v-if="!hasSubmitted && allQuestionsAnswered">
                <el-alert
                  title="您已完成所有题目的作答"
                  type="success"
                  :closable="false"
                  show-icon
                >
                  <p>请点击下方按钮提交所有答案</p>
                </el-alert>
                <el-button 
                  type="success" 
                  :loading="pendingSubmit"
                  @click="submitAllAnswers"
                  class="submit-all-btn"
                >
                  提交所有答案
                </el-button>
              </div>
              
              <!-- 答题记录和得分结果 -->
              <div v-if="hasSubmitted && currentEvaluation" class="evaluation-result">
                <h4>问题 {{ currentQuestionIndex + 1 }} 评价：</h4>
                
                <!-- 问题和用户答案 -->
                <div class="qa-record">
                  <div class="question-content">
                    <h5>问题内容：</h5>
                    <p>{{ questions[currentQuestionIndex]?.content || '加载中...' }}</p>
                  </div>
                  
                  <div class="user-answer">
                    <h5>您的答案：</h5>
                    <p>{{ userAnswers[questions[currentQuestionIndex]?.id] || '无答案' }}</p>
                  </div>
                </div>
                
                <!-- AI评价结果 -->
                <div class="score-header">
                  <span>得分：{{ currentEvaluation.score }}</span>
                  <el-tag 
                    :type="currentEvaluation.score >= 80 ? 'success' : currentEvaluation.score >= 60 ? 'warning' : 'danger'"
                  >
                    {{ currentEvaluation.level || '等级未知' }}
                  </el-tag>
                </div>
                <div class="score">
                  <el-progress 
                    :percentage="currentEvaluation.score" 
                    :status="currentEvaluation.score >= 80 ? 'success' : currentEvaluation.score >= 60 ? 'warning' : 'exception'"
                  ></el-progress>
                </div>
                <div class="feedback">
                  <h5>评价反馈：</h5>
                  <p>{{ currentEvaluation.feedback || '暂无评价' }}</p>
                </div>
                
                <div class="next-actions">
                  <el-button type="success" @click="nextQuestion" v-if="hasNextQuestion">
                    查看下一题评价
                  </el-button>
                  <el-button type="warning" @click="finishSession" v-else>
                    完成学习
                  </el-button>
                </div>
              </div>
              
              <!-- 答题进度 -->
              <div class="answer-progress" v-if="!hasSubmitted">
                <div class="progress-label">
                  <span>答题进度:</span>
                  <span>{{ Object.keys(userAnswers).length }}/{{ questions.length }}</span>
                </div>
                <el-progress 
                  :percentage="questions.length ? (Object.keys(userAnswers).length / questions.length) * 100 : 0"
                  :stroke-width="15"
                ></el-progress>
              </div>
              
              <!-- 已提交后显示总体得分 -->
              <div class="total-score" v-if="hasSubmitted && submissionResults.length > 0">
                <h4>总体得分</h4>
                <div class="score-average">
                  <span class="score-value">{{ calculateAverageScore() }}</span>
                  <span class="score-max">/100</span>
                </div>
                <el-progress 
                  type="circle" 
                  :percentage="calculateAverageScore()" 
                  :status="calculateAverageScore() >= 80 ? 'success' : calculateAverageScore() >= 60 ? 'warning' : 'exception'"
                ></el-progress>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </app-layout>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watchEffect, nextTick } from 'vue' 
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElAlert } from 'element-plus'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'
import { useUserStore } from '../../stores/user'

// 导入语音识别所需的依赖
import '../../../public/voice-utils/utilJS/crypto-js.js'
import '../../../public/voice-utils/utilJS/index.umd.js'
import VoiceRecognizer from '../../utils/VoiceRecognizer'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const courseId = computed(() => route.params.id)

// 状态
const loading = ref(false)
const course = ref(null)
const questions = ref([])
const currentQuestionIndex = ref(0)
const userAnswers = ref({}) // 存储所有题目的答案
const userAnswer = ref('') // 当前正在编辑的答案
const isSubmitting = ref(false)
const currentEvaluation = ref(null)
const answeredQuestions = ref([]) // 已回答的问题ID列表
const allQuestionsAnswered = ref(false) // 是否所有题目都已回答
const pendingSubmit = ref(false) // 是否等待提交所有答案
const submissionResults = ref([]) // 存储所有题目的评估结果
const hasSubmitted = ref(false) // 是否已经提交过所有答案

// 语音识别状态
const recognizer = ref(null)
const isRecording = ref(false)
const voiceStatus = ref('')
const voiceError = ref('')

// 数字人视频相关
const videoPlayer = ref(null)
const digitalHumanVideoUrl = ref('')
const isVideoLoaded = ref(false)
const isPlaying = ref(false)
const currentVideoUrl = ref('') // 当前播放的视频 URL
const showStartDialog = ref(true) // 显示开始测试提示框
const isTestStarting = ref(false); // 控制“开始测试”按钮的状态
const isVideoGenerationPending = ref(false); // 控制“正在准备视频...”按钮的状态

// 计算属性
const currentQuestion = computed(() => {
  if (questions.value.length === 0) return null
  return questions.value[currentQuestionIndex.value]
})

const hasNextQuestion = computed(() => 
  currentQuestionIndex.value < questions.value.length - 1
)



// 获取课程信息
const fetchCourse = async () => {
  try {
    const response = await axios.get(`/api/courses/${courseId.value}`)
    course.value = response.data.course
  } catch (error) {
    console.error('获取课程信息失败', error)
    ElMessage.error('获取课程信息失败')
  }
}

// 获取课程问题
const fetchQuestions = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/courses/${courseId.value}/questions`)
    questions.value = response.data.questions || []
    
    if (questions.value.length === 0) {
      ElMessage.info('该课程暂无问题')
    } else {
      // 获取学生已回答的问题
      await fetchAnsweredQuestions()
    }
  } catch (error) {
    console.error('获取问题失败', error)
    ElMessage.error('获取问题失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

// 获取已回答的问题
const fetchAnsweredQuestions = async () => {
  try {
    const response = await axios.get(`/api/courses/${courseId.value}/my-answers`)
    if (response.data.answers) {
      // 提取已回答问题的ID
      answeredQuestions.value = response.data.answers.map(answer => answer.question_id)
      
      // 检查是否所有问题都已回答
      checkAllQuestionsAnswered()
    }
  } catch (error) {
    console.error('获取已回答问题失败', error)
  }
}

// 检查是否所有问题都已回答
const checkAllQuestionsAnswered = () => {
  if (questions.value.length === 0) return
  
  // 检查是否所有问题都已经答过了
  allQuestionsAnswered.value = questions.value.every(question => 
    answeredQuestions.value.includes(question.id) || userAnswers.value[question.id]
  )
}

// // (可选) 修改 startTest 成功后的逻辑，加载第一个视频
// const startTest = async () => {
//   showStartDialog.value = false
//   isVideoGenerationPending.value = true;
//   try {
//     const response = await axios.post(`/api/courses/${courseId.value}/generate_question_videos`);
//     if (response.data.success && response.data.questions.length > 0) {
//       ElMessage.success('视频生成成功！');
//       questions.value = response.data.questions; 
      
//       // 可以在这里设置第一个问题的视频URL，但不自动播放
//       if (questions.value[0] && questions.value[0].video_url) {
//          currentVideoUrl.value = questions.value[0].video_url;
//          // 不在此处调用 play()，让用户点击开始或题目时再播放
//       }
//     } else {
//       ElMessage.error(response.data.message || '视频生成失败或没有问题');
//     }
//   } catch (error) {
//     console.error('视频生成失败', error);
//     ElMessage.error('视频生成失败，请稍后再试');
//   } finally {
//     isVideoGenerationPending.value = false;
//   }
// };

const startTest = async () => {
  // 开始测试时，将状态切换
  isTestStarting.value = true;
  isVideoGenerationPending.value = true;

  
  
  try {
    const response = await axios.post(`/api/courses/${courseId.value}/generate_question_videos`);
    
    if (response.data.success && response.data.questions.length > 0) {
      showStartDialog.value = false; // 关闭开始测试对话框
      // 视频生成成功
      ElMessage.success('视频生成成功！');
      
      questions.value = response.data.questions; 
      
      // 设置第一个问题的视频URL（但不自动播放，除非后续逻辑决定）
      if (questions.value[0] && questions.value[0].video_url) {
         currentVideoUrl.value = questions.value[0].video_url;
         // 这里不播放视频，用户点击开始或题目时再播放
      }
    } else {
      // 视频生成失败
      ElMessage.error(response.data.message || '视频生成失败或没有问题');
    }
  } catch (error) {
    console.error('视频生成失败', error);
    ElMessage.error('视频生成失败，请稍后再试');
  } finally {
    // 完成测试后，重置状态
    isVideoGenerationPending.value = false;
    isTestStarting.value = false; // 恢复按钮可用
  }
};


// 选择问题并播放视频
const selectQuestion = async (index) => { // 改为 async
  if (isSubmitting.value) return;

  // 保存当前问题的答案 (这部分逻辑不变)
  if (currentQuestion.value && userAnswer.value.trim()) {
    userAnswers.value[currentQuestion.value.id] = userAnswer.value;
    checkAllQuestionsAnswered();
  }

  // 切换到新的问题 (这部分逻辑不变)
  currentQuestionIndex.value = index;
  currentEvaluation.value = null;
  if (questions.value[index] && userAnswers.value[questions.value[index].id]) {
    userAnswer.value = userAnswers.value[questions.value[index].id];
  } else {
    userAnswer.value = '';
  }

  // --- 修改开始 ---
  const selectedQuestion = questions.value[index];
  
  // 检查问题是否有视频 URL
  if (selectedQuestion && selectedQuestion.video_url) {
    // 1. 更新视频播放器的 src
    currentVideoUrl.value = selectedQuestion.video_url;
    
    // 2. 等待 DOM 更新（src 应用到 video 元素）
    await nextTick(); 

    // 3. 使用 ref 控制播放器
    if (videoPlayer.value) {
      try {
        // videoPlayer.value.load(); // 显式加载新源 (有时需要)
        await videoPlayer.value.play(); // 尝试播放
        isPlaying.value = true; // 更新播放状态
      } catch (error) {
        console.error("视频播放失败:", error);
        // 用户可能需要手动点击播放，特别是浏览器限制自动播放时
        ElMessage.warning('视频可能需要手动点击播放');
        isPlaying.value = false; // 播放失败，重置状态
      }
    } else {
       console.warn("videoPlayer ref 尚未准备好");
    }
  } else {
    // 如果没有视频 URL，可以选择暂停或显示提示
    console.log(`问题 ${selectedQuestion?.id || index} 没有关联的视频 URL`);
    currentVideoUrl.value = ''; // 清空 URL
    if(videoPlayer.value) {
      videoPlayer.value.pause(); // 暂停播放器
    }
    isPlaying.value = false;
  }
  // --- 修改结束 ---
};

// 播放视频的逻辑
const playVideo = (questionId) => {
  const videoPlayer = document.getElementById(`video-player-${questionId}`); // 获取视频元素
  if (videoPlayer && videoPlayer.src) {
    videoPlayer.play();  // 播放视频
    isPlaying.value = true;  // 设置播放状态
  }
};

// 修改 toggleVideo 函数以使用 ref
const toggleVideo = () => {
  // 使用模板中的 ref 'videoPlayer'
  if (videoPlayer.value) {
    if (videoPlayer.value.paused) {
      videoPlayer.value.play().then(() => {
         isPlaying.value = true;
      }).catch(err => {
         console.error("手动播放失败:", err);
         ElMessage.error("无法播放视频");
      });
    } else {
      videoPlayer.value.pause();
      isPlaying.value = false;
    }
  } else {
     console.warn("videoPlayer ref 不可用");
  }
};

// 处理视频加载错误
const handleVideoError = (error) => {
  console.error('视频加载错误', error);
  ElMessage.error('视频加载失败');
};

// 处理视频加载完成
const handleVideoLoaded = () => {
  isPlaying.value = true;
};



// 暂存当前答案
const saveCurrentAnswer = () => {
  if (currentQuestion.value && userAnswer.value.trim()) {
    userAnswers.value[currentQuestion.value.id] = userAnswer.value
    ElMessage.success('已保存当前答案')
    
    // 检查是否所有问题都已回答
    checkAllQuestionsAnswered()
  } else {
    ElMessage.warning('请输入答案后保存')
  }
}

// 移动到下一题并保存当前答案
const moveToNextWithSave = () => {
  if (currentQuestion.value && userAnswer.value.trim()) {
    userAnswers.value[currentQuestion.value.id] = userAnswer.value
    
    // 检查是否所有问题都已回答
    checkAllQuestionsAnswered()
  }
  
  if (hasNextQuestion.value) {
    selectQuestion(currentQuestionIndex.value + 1)
  } else {
    ElMessage.info('这是最后一个问题了')
  }
}

// 跳转到下一题
const nextQuestion = () => {
  if (hasNextQuestion.value) {
    // 如果已经提交过所有答案，则直接切换到下一个问题的评估结果
    if (hasSubmitted.value) {
      const nextIndex = currentQuestionIndex.value + 1;
      currentQuestionIndex.value = nextIndex;
      
      // 查找下一个问题的评估结果
      if (questions.value[nextIndex]) {
        const nextQuestionId = questions.value[nextIndex].id;
        const nextResult = submissionResults.value.find(r => r.question_id === nextQuestionId);
        if (nextResult) {
          currentEvaluation.value = nextResult;
        } else {
          console.log(`未找到问题ID ${nextQuestionId} 的评估结果`);
          // 尝试通过索引获取结果
          if (submissionResults.value.length > nextIndex) {
            console.log('使用索引获取评估结果');
            currentEvaluation.value = submissionResults.value[nextIndex];
          } else {
            // 如果没有找到下一个问题的评估结果，清空当前评估
            currentEvaluation.value = null;
          }
        }
      }
    } else {
      // 否则保存当前答案并移动到下一题
      selectQuestion(currentQuestionIndex.value + 1);
    }
  } else {
    finishSession();
  }
}

// 跳过当前问题
const skipQuestion = () => {
  if (hasNextQuestion.value) {
    ElMessage.info('已跳过当前问题')
    selectQuestion(currentQuestionIndex.value + 1)
  } else {
    ElMessage.info('这是最后一个问题了')
  }
}

// 完成答题
const finishSession = () => {
  // 如果有未提交的答案，提示用户
  if (!hasSubmitted.value && allQuestionsAnswered.value) {
    ElMessageBox.confirm(
      '您已回答所有问题但尚未提交，是否提交所有答案？',
      '提示',
      {
        confirmButtonText: '提交答案',
        cancelButtonText: '返回课程',
        type: 'warning',
      }
    )
      .then(() => {
        submitAllAnswers().then(() => {
          router.push(`/courses/${courseId.value}`)
        })
      })
      .catch(() => {
        router.push(`/courses/${courseId.value}`)
      })
  } else {
    router.push(`/courses/${courseId.value}`)
  }
}

// 初始化语音识别
const initVoiceRecognition = () => {
  try {
    // 检查识别器是否已存在
    if (recognizer.value) {
      return;
    }
    
    // 创建语音识别器实例
    recognizer.value = new VoiceRecognizer({
      appId: 'e1781d1b', 
      apiKey: '5956b81de861e15997eb7c39f99f9a5b', 
      apiSecret: 'MDA0YzNhMTNlOTYzMWM5ZTNmOTJjMTg4', 
      language: 'zh_cn',
      accent: 'mandarin',
      maxReconnect: 3,
      
      onResult: function(text, isFinal) {
        if (text && text.trim()) {
          // 不覆盖现有答案，而是将新文本追加到现有答案后
          if (userAnswer.value) {
            userAnswer.value = userAnswer.value + text;
          } else {
            userAnswer.value = text;
          }
        }
      },
      onStart: function() {
        isRecording.value = true;
        ElMessage.info('开始语音输入');
      },
      onStop: function(finalText) {
        isRecording.value = false;
        if (finalText && finalText.trim() && !userAnswer.value.includes(finalText)) {
          // 防止重复添加相同的文本
          if (userAnswer.value) {
            userAnswer.value = userAnswer.value + ' ' + finalText;
          } else {
            userAnswer.value = finalText;
          }
        }
        ElMessage.success('语音输入完成');
        
        // 将当前答案保存到userAnswers中
        if (currentQuestion.value && userAnswer.value.trim()) {
          userAnswers.value[currentQuestion.value.id] = userAnswer.value;
          checkAllQuestionsAnswered();
        }
      },
      onError: function(message) {
        voiceError.value = message;
        isRecording.value = false;
        ElMessage.error('语音识别错误: ' + message);
      },
      onStatusChange: function(status) {
        voiceStatus.value = status;
      }
    });
    
    // 修正录音管理器初始化路径
    const distPath = '/voice-utils/dist';
    
    console.log('正在初始化录音管理器，路径:', distPath);
    const initResult = recognizer.value.initRecorder(distPath);
    if (!initResult) {
      ElMessage.error('录音管理器初始化失败');
    } else {
      console.log('录音管理器初始化成功');
    }
  } catch (error) {
    console.error('初始化语音识别失败:', error);
    ElMessage.error('初始化语音识别功能失败: ' + error.message);
  }
}

// 切换语音识别
const toggleVoiceRecognition = () => {
  if (isRecording.value) {
    stopVoiceRecognition();
    return;
  }
  
  if (!recognizer.value) {
    initVoiceRecognition();
    // 初始化后短暂延迟再启动录音
    setTimeout(() => {
      startVoiceRecognition();
    }, 500);
    return;
  }
  
  startVoiceRecognition();
}

// 开始语音识别
const startVoiceRecognition = () => {
  if (!recognizer.value) {
    ElMessage.warning('语音识别组件未初始化，请稍后再试');
    return;
  }
  
  console.log('开始语音识别...');
  recognizer.value.start().then(() => {
    console.log('语音识别已启动');
  }).catch(error => {
    console.error('启动语音识别失败:', error);
    ElMessage.error('启动语音识别失败: ' + error.message);
    isRecording.value = false;
  });
}

// 停止语音识别
const stopVoiceRecognition = () => {
  if (!recognizer.value) return;
  recognizer.value.stop();
}

// // 开始测试
// const startTest = () => {
//   showStartDialog.value = false
//   // 延迟一小段时间后开始播放视频
//   setTimeout(() => {
//     if (videoPlayer.value) {
//       videoPlayer.value.play()
//         .then(() => {
//           isPlaying.value = true
//           console.log('视频开始播放')
//         })
//         .catch(err => {
//           console.error('视频播放失败:', err)
//           ElMessage.warning('视频播放失败，请点击播放按钮手动播放')
//         })
//     }
//   }, 500)
// }

// // 切换视频播放/暂停
// const toggleVideo = () => {
//   if (!videoPlayer.value) return
  
//   if (isPlaying.value) {
//     videoPlayer.value.pause()
//     isPlaying.value = false
//   } else {
//     videoPlayer.value.play()
//       .then(() => {
//         isPlaying.value = true
//       })
//       .catch(err => {
//         console.error('视频播放失败:', err)
//         ElMessage.warning('视频播放失败，请重试')
//       })
//   }
// }

// // 视频事件处理
// const handleVideoError = (event) => {
//   console.error('视频加载错误:', event)
//   isVideoLoaded.value = false
// }

// const handleVideoLoaded = () => {
//   console.log('视频加载成功')
//   isVideoLoaded.value = true
// }

// 页面加载
onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([fetchCourse(), fetchQuestions()])
    console.log('课程和问题加载完成')
    if (questions.value.length > 0) {
      console.log(`加载了 ${questions.value.length} 个问题`)
    } else {
      console.log('没有找到任何问题')
    }
    initVoiceRecognition()
  } catch (error) {
    console.error('初始化页面时出错:', error)
  } finally {
    loading.value = false
  }
})

// 页面卸载前清理
onBeforeUnmount(() => {
  // 停止视频播放
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    isPlaying.value = false
  }
  
  // 释放视频Blob URL
  if (digitalHumanVideoUrl.value && digitalHumanVideoUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(digitalHumanVideoUrl.value)
  }
  
  if (recognizer.value) {
    recognizer.value.stop()
  }
})

// 计算平均得分
const calculateAverageScore = () => {
  if (!submissionResults.value || submissionResults.value.length === 0) return 0;
  let totalScore = 0;
  let count = 0;
  
  submissionResults.value.forEach(result => {
    if (result && typeof result.score === 'number') {
      totalScore += result.score;
      count++;
    }
  });
  
  return count > 0 ? Math.round(totalScore / count) : 0;
}

// 提交所有答案
const submitAllAnswers = async () => {
  if (!allQuestionsAnswered.value) {
    ElMessage.warning('请先回答所有问题')
    return
  }
  
  pendingSubmit.value = true
  submissionResults.value = [] // 清空之前的结果
  
  try {
    // 准备要提交的问题列表
    const questionsToSubmit = questions.value.filter(q => 
      userAnswers.value[q.id] && !answeredQuestions.value.includes(q.id)
    )
    
    if (questionsToSubmit.length === 0) {
      ElMessage.info('所有答案已经提交过了')
      hasSubmitted.value = true
      pendingSubmit.value = false
      return
    }
    
    console.log(`准备提交 ${questionsToSubmit.length} 个答案`)
    
    // 逐个提交答案
    const results = []
    const failedSubmissions = []
    
    // 使用索引记录问题顺序
    let index = 0
    for (const question of questionsToSubmit) {
      let retryCount = 0
      const maxRetries = 2 // 最多重试2次
      let submitted = false
      
      while (!submitted && retryCount <= maxRetries) {
        try {
          if (retryCount > 0) {
            console.log(`重试提交问题 ${question.id} 的答案 (第${retryCount}次)`)
          } else {
            console.log(`正在提交问题 ${question.id} 的答案`)
          }
          
          // 使用现有的API端点，确保URL前缀正确
          const response = await axios.post(`/api/questions/${question.id}/answer`, {
            answer: userAnswers.value[question.id]
          })
          
          if (response.data.success) {
            console.log(`问题 ${question.id} 提交成功`)
            // 保存评估结果，包含问题序号和ID信息
            results.push({
              question_id: question.id,
              question_index: index,  // 保存问题的索引
              ...response.data.evaluation
            })
            
            // 将问题ID添加到已回答列表
            if (!answeredQuestions.value.includes(question.id)) {
              answeredQuestions.value.push(question.id)
            }
            
            submitted = true
          } else {
            console.error(`问题 ${question.id} 提交失败:`, response.data.message)
            retryCount++
            
            if (retryCount > maxRetries) {
              failedSubmissions.push({
                id: question.id,
                reason: response.data.message || '服务器返回失败'
              })
            } else {
              // 等待一段时间再重试
              await new Promise(resolve => setTimeout(resolve, 1000))
            }
          }
        } catch (error) {
          console.error(`问题 ${question.id} 提交出错:`, error)
          retryCount++
          
          if (retryCount > maxRetries) {
            failedSubmissions.push({
              id: question.id,
              reason: error.message || '网络错误'
            })
          } else {
            // 等待一段时间再重试
            await new Promise(resolve => setTimeout(resolve, 1000))
          }
        }
      }
      index++
    }
    
    // 按照问题序号排序结果
    submissionResults.value = results.sort((a, b) => a.question_index - b.question_index)
    
    if (results.length > 0) {
      hasSubmitted.value = true
      
      if (failedSubmissions.length > 0) {
        // 部分成功，部分失败
        ElMessageBox.alert(
          `成功提交: ${results.length} 题<br>` +
          `失败: ${failedSubmissions.length} 题<br><br>` +
          `失败的题目: ${failedSubmissions.map(f => `#${f.id}`).join(', ')}<br>` +
          `原因可能是服务器暂时性错误，请稍后再试。`,
          '部分答案提交成功',
          {
            confirmButtonText: '确定',
            dangerouslyUseHTMLString: true,
            type: 'warning'
          }
        )
      } else {
        // 全部成功
        ElMessage.success('所有答案提交成功！')
      }
      
      // 显示第一个问题的评估结果
      currentQuestionIndex.value = 0
      if (results.length > 0) {
        // 首先尝试找到第一个问题的评估结果
        const firstQuestionId = questions.value[0].id
        const firstResult = results.find(r => r.question_id === firstQuestionId)
        
        if (firstResult) {
          console.log('找到第一个问题的评估结果')
          currentEvaluation.value = firstResult
        } else {
          // 如果找不到，使用第一个结果
          console.log('使用第一个提交的结果')
          currentEvaluation.value = results[0]
          
          // 找到对应的问题索引
          const questionIndex = questions.value.findIndex(q => q.id === results[0].question_id)
          if (questionIndex >= 0) {
            currentQuestionIndex.value = questionIndex
          }
        }
      }
    } else {
      // 全部失败
      ElMessageBox.alert(
        `所有答案提交失败<br><br>` +
        `可能原因:<br>` +
        `1. 服务器暂时不可用<br>` +
        `2. 网络连接问题<br>` +
        `3. 服务器内部错误<br><br>` +
        `请稍后再试或联系管理员。`,
        '提交失败',
        {
          confirmButtonText: '确定',
          dangerouslyUseHTMLString: true,
          type: 'error'
        }
      )
    }
  } catch (error) {
    console.error('提交所有答案失败', error)
    ElMessage.error('提交失败，请稍后再试')
  } finally {
    pendingSubmit.value = false
  }
}

// 退出登录
const logout = async () => {
  try {
    const result = await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    if (result === 'confirm') {
      const logoutResult = await userStore.logout()
      if (logoutResult.success) {
        ElMessage.success('退出成功')
        router.push('/login')
      } else {
        ElMessage.error(logoutResult.message || '退出失败')
      }
    }
  } catch (e) {
    // 用户取消操作
  }
}
</script>

<style scoped>
.ai-assistant-page {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.ai-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.content-container {
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

/* 数字人视频卡片 */
.digital-human-section {
  margin-bottom: 20px;
}

.digital-human-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #f0f5ff, #e6f7ff);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #e6e6e6;
}

.card-header h3 {
  margin: 0;
  color: #1a1a1a;
  font-size: 18px;
  font-weight: 600;
}

.video-container {
  background-color: #000;
  display: flex;
  justify-content: center;
  position: relative;
}

.video-wrapper {
  width: 100%;
  background-color: #000;
  overflow: hidden;
  position: relative;
}

.digital-human-video {
  width: 100%;
  height: auto;
  min-height: 350px;
  max-height: 450px;
  object-fit: contain;
  display: block;
}

.digital-human-info {
  padding: 12px 15px;
  text-align: center;
  background-color: #f9f9f9;
  border-top: 1px solid #e6e6e6;
}

.digital-human-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.video-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  z-index: 1;
}

@media (min-width: 992px) {
  .content-container {
    flex-direction: row;
    gap: 20px;
  }
  
  .digital-human-section {
    width: 35%;
    margin-bottom: 0;
  }
  
  .qa-section {
    width: 65%;
  }
}

/* 答题区域 */
.qa-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.course-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.course-info-header h3 {
  margin: 0;
  font-size: 18px;
}

.question-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.question-card {
  margin-bottom: 20px;
}

.question-card h4 {
  margin: 15px 0 5px;
  color: #303133;
}

/* 答案输入容器 */
.answer-input-container {
  position: relative;
  margin-bottom: 15px;
}

.answer-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.evaluation-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.score {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}

.feedback {
  margin: 15px 0;
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
}

.next-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.no-questions {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 语音输入样式 */
.voice-input-controls {
  position: absolute;
  right: 10px;
  bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.voice-icon {
  width: 20px;
  height: 20px;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12,2c-1.1,0-2,0.9-2,2v8c0,1.1,0.9,2,2,2s2-0.9,2-2V4C14,2.9,13.1,2,12,2z M17.3,10.8c0,3-2.5,5.3-5.3,5.3c-2.8,0-5.3-2.3-5.3-5.3h-2c0,3.7,2.8,6.8,6.5,7.3V22h2v-3.9c3.7-0.4,6.5-3.5,6.5-7.3H17.3z"/></svg>');
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  display: inline-block;
}

.voice-icon.recording {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="red"><path d="M12,2c-1.1,0-2,0.9-2,2v8c0,1.1,0.9,2,2,2s2-0.9,2-2V4C14,2.9,13.1,2,12,2z M17.3,10.8c0,3-2.5,5.3-5.3,5.3c-2.8,0-5.3-2.3-5.3-5.3h-2c0,3.7,2.8,6.8,6.5,7.3V22h2v-3.9c3.7-0.4,6.5-3.5,6.5-7.3H17.3z"/></svg>');
  animation: pulse 1.5s infinite;
}

.recording-text {
  color: #f56c6c;
  font-size: 14px;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    opacity: 1;
  }
}

.el-button.is-recording {
  background-color: #f56c6c;
  border-color: #f56c6c;
  color: white;
}

.answered-tag {
  margin-top: 10px;
}

.answer-progress {
  margin-top: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.progress-label {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.submit-all-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.submit-all-btn {
  margin-top: 10px;
}

.total-score {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.score-average {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  margin-bottom: 10px;
}

.score-value {
  font-size: 18px;
  font-weight: bold;
}

.score-max {
  font-size: 14px;
}

@media (max-width: 768px) {
  .qa-section {
    width: 100%;
  }
}

.qa-record {
  margin: 15px 0;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.question-content, .user-answer {
  margin-bottom: 15px;
}

.question-content h5, .user-answer h5, .feedback h5 {
  font-size: 15px;
  margin: 0 0 8px 0;
  color: #606266;
}

.user-answer {
  background-color: #f0f9eb;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.user-answer p {
  white-space: pre-wrap;
  word-break: break-word;
}

/* 题目导航 */
.question-navigation {
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 15px;
}

.question-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.question-buttons .el-button {
  margin: 0;
}

.question-buttons .answered {
  position: relative;
}

.question-buttons .answered::after {
  content: '✓';
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #67C23A;
  color: white;
  width: 16px;
  height: 16px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.video-controls-container {
  display: flex;
  justify-content: center;
  padding: 10px 0;
  background-color: #f0f0f0;
  border-top: 1px solid #ddd;
}

.video-control-btn {
  font-size: 18px;
  width: 54px;
  height: 54px;
}

.start-dialog-content {
  text-align: center;
  padding: 20px 0;
}

.dialog-footer {
  display: flex;
  justify-content: center;
}
</style> 