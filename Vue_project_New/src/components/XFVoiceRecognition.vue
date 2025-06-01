<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import VoiceRecognizer from '../utils/VoiceRecognizer';

// 组件属性
const props = defineProps({
  appId: {
    type: String,
    required: true
  },
  apiKey: {
    type: String,
    required: true
  },
  apiSecret: {
    type: String,
    required: true
  },
  recorderPath: {
    type: String,
    default: '/voice-utils/dist'
  },
  language: {
    type: String,
    default: 'zh_cn'
  },
  accent: {
    type: String,
    default: 'mandarin'
  },
  maxReconnect: {
    type: Number,
    default: 3
  }
});

// 组件事件
const emit = defineEmits([
  'result', // 识别结果
  'start', // 开始识别
  'stop', // 停止识别
  'error', // 错误
  'status-change' // 状态变化
]);

// 状态变量
const recognizer = ref(null);
const recognizing = ref(false);
const buttonText = ref('点击开始语音识别');
const recognizedText = ref('');
const errorMessage = ref('');

// 初始化语音识别器
onMounted(() => {
  initRecognizer();
});

// 清理资源
onBeforeUnmount(() => {
  if (recognizer.value) {
    try {
      recognizer.value.stop();
    } catch (error) {
      console.error('停止语音识别失败:', error);
    }
  }
});

// 初始化语音识别器
function initRecognizer() {
  try {
    // 创建语音识别器实例
    recognizer.value = new VoiceRecognizer({
      appId: props.appId,
      apiKey: props.apiKey,
      apiSecret: props.apiSecret,
      language: props.language,
      accent: props.accent,
      maxReconnect: props.maxReconnect,
      
      // 回调函数
      onResult: (text, isFinal) => {
        recognizedText.value = text;
        emit('result', { text, isFinal });
      },
      onStart: () => {
        recognizing.value = true;
        buttonText.value = '点击停止识别';
        errorMessage.value = '';
        emit('start');
      },
      onStop: (finalText) => {
        recognizing.value = false;
        buttonText.value = '点击开始语音识别';
        emit('stop', finalText);
      },
      onError: (message) => {
        errorMessage.value = message;
        emit('error', message);
      },
      onStatusChange: (status) => {
        switch (status) {
          case 'CONNECTING':
            buttonText.value = '正在连接...';
            break;
          case 'OPEN':
            buttonText.value = '正在录音，点击停止';
            break;
          case 'CLOSED':
            buttonText.value = '点击开始语音识别';
            recognizing.value = false;
            break;
        }
        emit('status-change', status);
      }
    });
    
    // 初始化录音管理器
    const initResult = recognizer.value.initRecorder(props.recorderPath);
    if (!initResult) {
      errorMessage.value = '录音管理器初始化失败';
    }
  } catch (error) {
    console.error('初始化语音识别器失败:', error);
    errorMessage.value = '初始化语音识别器失败: ' + error.message;
  }
}

// 切换识别状态
function toggleRecognition() {
  if (!recognizer.value) {
    errorMessage.value = '语音识别器未初始化';
    return;
  }
  
  if (recognizing.value) {
    stopRecognition();
  } else {
    startRecognition();
  }
}

// 开始识别
function startRecognition() {
  errorMessage.value = '';
  recognizer.value.start().catch(error => {
    console.error('启动语音识别失败:', error);
    errorMessage.value = '启动语音识别失败: ' + error.message;
  });
}

// 停止识别
function stopRecognition() {
  recognizer.value.stop();
}

// 清空识别结果
function clearResult() {
  recognizedText.value = '';
  emit('result', { text: '', isFinal: true });
}

// 暴露组件方法供父组件调用
defineExpose({
  start: startRecognition,
  stop: stopRecognition,
  clear: clearResult
});
</script>

<template>
  <div class="xf-voice-recognition">
    <!-- 录音按钮 -->
    <div class="recognition-button">
      <button 
        class="recognition-btn"
        :class="{ 'recognizing': recognizing }"
        @click="toggleRecognition">
        {{ buttonText }}
      </button>
    </div>
    
    <!-- 错误消息 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    
    <!-- 识别结果 -->
    <div class="recognition-result">
      <div v-if="recognizedText" class="result-content">
        {{ recognizedText }}
      </div>
      <div v-else class="placeholder">
        语音识别结果将显示在这里
      </div>
      <button 
        v-if="recognizedText" 
        class="clear-btn"
        @click="clearResult">
        清空
      </button>
    </div>
  </div>
</template>

<style scoped>
.xf-voice-recognition {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.recognition-button {
  margin-bottom: 20px;
}

.recognition-btn {
  padding: 10px 20px;
  border-radius: 50px;
  background-color: #0B51DB;
  color: white;
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 180px;
}

.recognition-btn:hover {
  background-color: #0941b3;
}

.recognition-btn.recognizing {
  background-color: #e74c3c;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.error-message {
  color: #e74c3c;
  margin: 10px 0;
  padding: 10px;
  background-color: #fceaea;
  border-radius: 4px;
  width: 100%;
  text-align: center;
}

.recognition-result {
  width: 100%;
  min-height: 100px;
  margin-top: 20px;
  padding: 15px;
  background-color: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  position: relative;
}

.result-content {
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 30px;
}

.placeholder {
  color: #999;
  text-align: center;
  margin: 20px 0;
}

.clear-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  padding: 4px 12px;
  background-color: #f2f2f2;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.clear-btn:hover {
  background-color: #e6e6e6;
}
</style> 