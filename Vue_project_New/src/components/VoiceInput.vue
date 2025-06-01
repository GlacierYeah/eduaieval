<script setup>
import { ref, onMounted } from "vue../../../Vue_project/src/voice-utils/utilJS/crypto-js.js 'element-pl../../../Vue_project/src/voice-utils/utilJS/index.umd.jsS/crypto-js.js';
import '../voice-utils/utilJS/index.umd.js';

const btnText = ref("点击开始说话");
const btnStatus = ref("UNDEFINED"); // "UNDEFINED" "CONNECTING" "OPEN" "CLOSING" "CLOSED"
const recorder = new RecorderManager('/src/voice-utils/dist');
const APPID = "e1781d1b"; // 讯飞模型APPID
const API_SECRET = "MDA0YzNhMTNlOTYzMWM5ZTNmOTJjMTg4"; // 讯飞模型API_SECRET
const API_KEY = "5956b81de861e15997eb7c39f99f9a5b"; // 讯飞模型API_KEY
let iatWS; // 监听录音的变量

const resultText = ref(''); // 识别结果
const resultTextTemp = ref('');
let countdownInterval;
const message = ref('');
const ChatListy = ref([]);

// 添加连接状态变量和重连计数器
let reconnectCount = 0;
const MAX_RECONNECT = 3;
let willReconnect = false;

// 错误提示消息
const errorMessages = {
  microphoneAccessDenied: "无法访问麦克风。请确保您已授予浏览器麦克风访问权限，并且没有其他应用程序正在使用麦克风。",
  connectionFailed: "连接服务器失败，请检查网络连接并重试。",
  recognitionError: "语音识别出错，请重试。"
};

onMounted(() => {
  // 初始化聊天记录
  ChatListy.value.push({
    role: 'Ai',
    text: "请点击按钮开始语音识别",
    time: getCurrentTime(),
  });
  
  // 添加窗口关闭事件
  window.addEventListener('beforeunload', resetConnection);
});

// 获取当前时间
function getCurrentTime() {
  const now = new Date();
  return `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
}

// 生成 WebSocket URL 生成规则由平台决定
function getWebSocketUrl() {
  // 请求地址根据语种不同变化
  var url = "wss://iat-api.xfyun.cn/v2/iat";
  var host = "iat-api.xfyun.cn";
  var apiKey = API_KEY;
  var apiSecret = API_SECRET;
  var date = new Date().toGMTString();
  var algorithm = "hmac-sha256";
  var headers = "host date request-line";
  var signatureOrigin = `host: ${host}\ndate: ${date}\nGET /v2/iat HTTP/1.1`;
  var signatureSha = CryptoJS.HmacSHA256(signatureOrigin, apiSecret);
  var signature = CryptoJS.enc.Base64.stringify(signatureSha);
  var authorizationOrigin = `api_key="${apiKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`;
  var authorization = btoa(authorizationOrigin);
  
  // 构建URL，确保URL中不包含common和business参数
  return `${url}?authorization=${authorization}&date=${date}&host=${host}`;
}

// 加密工具函数
function toBase64(buffer) {
  try {
    var binary = "";
    var bytes = new Uint8Array(buffer);
    var len = bytes.byteLength;
    for (var i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  } catch (e) {
    console.error("音频编码错误:", e);
    return "";
  }
}

// 计数函数
function countdown() {
  let seconds = 60;
  btnText.value = `正在录音，点击结束 (${seconds}s)`;
  countdownInterval = setInterval(() => {
    seconds = seconds - 1;
    if (seconds <= 0) {
      stopRecording();
    } else {
      btnText.value = `正在录音，点击结束 (${seconds}s)`;
    }
  }, 1000);
}

// 录音状态变化函数
function changeStatus(status) {
  btnStatus.value = status;
  if (status === "CONNECTING") {
    btnText.value = "建立连接中";
    resultText.value = '';
    resultTextTemp.value = "";
  } else if (status === "OPEN") {
    countdown();
  } else if (status === "CLOSING") {
    btnText.value = "关闭连接中";
  } else if (status === "CLOSED") {
    btnText.value = "点击开始说话";
  }
}

// 结果解析函数
function renderResult(resultData) {
  try {
    // 识别结束
    let jsonData = JSON.parse(resultData);
    
    console.log("解析结果:", jsonData);
    
    // 检查错误码
    if (jsonData.code !== 0) {
      console.error(`讯飞API错误: 代码 ${jsonData.code}, 消息: ${jsonData.message}, 会话ID: ${jsonData.sid}`);
      
      // 特定错误处理
      if (jsonData.code === 10165) {
        showError("会话ID无效，正在重新连接...");
        // 清理现有连接
        resetConnection();
        
        // 延迟2秒后重新尝试连接（避免频繁重连）
        setTimeout(() => {
          startRecording();
        }, 2000);
      } else {
        showError(`识别错误(${jsonData.code}): ${jsonData.message || errorMessages.recognitionError}`);
      }
      
      if (iatWS && iatWS.readyState === 1) {
        iatWS.close();
      }
      return;
    }
    
    // 正常处理识别结果
    if (jsonData.data && jsonData.data.result) {
      let data = jsonData.data.result;
      let str = "";
      
      // 确保ws字段存在且有内容
      if (data.ws && data.ws.length > 0) {
        let ws = data.ws;
        
        for (let i = 0; i < ws.length; i++) {
          // 确保cw字段存在且有内容
          if (ws[i].cw && ws[i].cw.length > 0) {
            // 检查识别结果是否为空
            let word = ws[i].cw[0].w;
            if (word && word.trim() !== "") {
              str += word;
            }
          }
        }
        
        // 检查是否有真正的内容
        if (str.trim() !== "") {
          console.log("识别到文字:", str);
          
          // 开启wpgs会有此字段(前提：在控制台开通动态修正功能)
          // 取值为 "apd"时表示该片结果是追加到前面的最终结果；取值为"rpl" 时表示替换前面的部分结果，替换范围为rg字段
          if (data.pgs) {
            if (data.pgs === "apd") {
              // 将resultTextTemp同步给resultText
              message.value = resultTextTemp.value;
            }
            // 将结果存储在resultTextTemp中
            resultTextTemp.value = message.value + str;
          } else {
            message.value = message.value + str;
          }
        } else if (data.ls && data.ls === true) {
          // 这是最后一个分段，但没有内容，可能是本次没有识别到任何有效语音
          console.log("本段未识别到有效语音");
        }
      } else if (data.ls && data.ls === true) {
        // 这是最后一个分段，但没有ws字段或ws为空
        console.log("本次识别已完成，但未识别到有效语音");
      }
    }
    
    // 会话结束
    if (jsonData.code === 0 && jsonData.data && jsonData.data.status === 2) {
      console.log("会话结束，当前识别文本:", message.value);
      
      // 检查最终是否有识别结果
      if (!message.value || message.value.trim() === "") {
        // 无识别结果，提示用户
        ElNotification({
          title: '提示',
          message: "未能识别到语音，请靠近麦克风并重试",
          type: 'warning',
          duration: 3000
        });
      }
      
      if (iatWS) {
        iatWS.close();
      }
    }
  } catch (error) {
    console.error("解析结果时出错:", error);
  }
}

// 显示错误通知
function showError(message) {
  ElNotification({
    title: '错误',
    message: message,
    type: 'error',
    duration: 5000
  });
  
  // 添加错误消息到聊天记录
  ChatListy.value.push({
    role: 'Ai',
    text: message,
    time: getCurrentTime(),
  });
}

// 连接 WebSocket
function connectWebSocket() {
  const websocketUrl = getWebSocketUrl();
  
  // 先确保之前的连接已关闭
  if (iatWS) {
    try {
      iatWS.close();
    } catch (error) {
      console.error("关闭之前的WebSocket连接出错:", error);
    }
    iatWS = null;
  }
  
  if ("WebSocket" in window) {
    try {
      iatWS = new WebSocket(websocketUrl);
      console.log("正在创建WebSocket连接...");
    } catch (error) {
      console.error("创建WebSocket连接失败:", error);
      showError("创建连接失败，请刷新页面重试");
      resetConnection();
      return;
    }
  } else if ("MozWebSocket" in window) {
    try {
      iatWS = new MozWebSocket(websocketUrl);
    } catch (error) {
      console.error("创建MozWebSocket连接失败:", error);
      showError("创建连接失败，请刷新页面重试");
      resetConnection();
      return;
    }
  } else {
    alert("浏览器不支持WebSocket");
    return;
  }
  
  changeStatus("CONNECTING");
  
  // 设置连接超时定时器
  const connectionTimeout = setTimeout(() => {
    if (btnStatus.value === "CONNECTING") {
      console.error("WebSocket连接超时");
      showError("连接超时，请检查网络后重试");
      closeWebSocketSafely();
      changeStatus("CLOSED");
    }
  }, 10000); // 10秒连接超时
  
  iatWS.onopen = () => {
    // 清除连接超时定时器
    clearTimeout(connectionTimeout);
    
    // 重置重连计数器
    reconnectCount = 0;
    willReconnect = false;
    
    // 先检查WebSocket连接状态
    if (!iatWS || iatWS.readyState !== 1) {
      console.error("WebSocket连接状态错误:", iatWS ? iatWS.readyState : "连接为空");
      showError("连接异常，请重试");
      if (iatWS) {
        try {
          iatWS.close();
        } catch (error) {}
      }
      resetConnection();
      return;
    }
    
    changeStatus("OPEN");
    
    // 连接建立后，立即发送初始帧 - 这是关键修复
    // 在WebSocket连接建立后，第一个消息必须是包含common和business参数的初始化帧
    try {
      const initParams = {
        common: {
          app_id: APPID
        },
        business: {
          language: "zh_cn",     // 中文普通话
          domain: "iat",         // 应用领域
          accent: "mandarin",    // 方言
          vad_eos: 10000,        // 静音检测时长，调大以避免过早结束
          ptt: 0,                // 标点符号
          dwa: "wpgs",           // 动态修正
        },
        data: {
          status: 0,             // 0表示初始帧
          format: "audio/L16;rate=16000",
          encoding: "raw",
          audio: ""
        }
      };
      
      console.log("正在发送初始化帧", initParams);
      // 二次检查WebSocket状态
      if (iatWS && iatWS.readyState === 1) {
        iatWS.send(JSON.stringify(initParams));
      } else {
        throw new Error("WebSocket连接已关闭，无法发送初始化帧");
      }
    } catch (error) {
      console.error("发送初始化帧出错:", error);
      showError("初始化连接失败，请重试");
      resetConnection();
      return;
    }
    
    // 开始录音
    // 使用Promise方式启动录音
    let isRecordingStarted = false;
    
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      recorder.onFrameRecorded = ({ isLastFrame, frameBuffer }) => {
        // 检查 WebSocket 状态和按钮状态，确保连接正常且处于录音状态
        if (!iatWS || iatWS.readyState !== 1) {
          console.log("WebSocket已关闭，丢弃音频帧");
          return;
        }
        
        if (btnStatus.value === "OPEN" && iatWS && iatWS.readyState === 1) { // 1 = OPEN
          // 最后一帧为空，结束
          if (isLastFrame && !frameBuffer) {
            try {
              iatWS.send(
                JSON.stringify({
                  data: {
                    status: 2, // 结束帧
                    format: "audio/L16;rate=16000",
                    encoding: "raw",
                    audio: ""
                  }
                })
              );
            } catch (error) {
              console.error("发送空帧时出错:", error);
            }
            return;
          }
          
          // 发送音频
          try {
            // 检查frameBuffer是否有效
            if (frameBuffer && frameBuffer.byteLength > 0) {
              const audio = toBase64(frameBuffer);
              // 仅在编码成功后发送
              if (audio) {
                iatWS.send(
                  JSON.stringify({
                    data: {
                      status: isLastFrame ? 2 : 1, // 1：中间帧，2：结束帧
                      format: "audio/L16;rate=16000",
                      encoding: "raw",
                      audio: audio
                    }
                  })
                );
              }
            } else {
              console.warn("收到空的音频帧");
            }
          } catch (error) {
            console.error("发送音频帧时出错:", error);
          }
        }
      };
      
      recorder.onStop = () => {
        // 如果录音没有做到最后，发送最后一帧
        if (btnStatus.value === "OPEN" && iatWS && iatWS.readyState === 1) { // 1 = OPEN
          try {
            iatWS.send(
              JSON.stringify({
                data: {
                  status: 2,
                  format: "audio/L16;rate=16000",
                  encoding: "raw",
                  audio: "",
                },
              })
            );
          } catch (error) {
            console.error("录音停止时发送最后一帧出错:", error);
          }
        }
      };
      
      // 使用Promise启动录音
      console.log("准备启动录音...");
      recorder.start({
        sampleRate: 16000,
        frameSize: 1280,
        arrayBufferType: "short16"
      }).then(() => {
        isRecordingStarted = true;
        console.log("录音启动成功");
        ElNotification({
          title: '提示',
          message: "录音已开始，请靠近麦克风说话",
          type: 'success',
          duration: 2000
        });
      }).catch(error => {
        console.error("启动录音失败:", error);
        showError(errorMessages.microphoneAccessDenied);
        resetConnection();
      });
      
      // 设置安全超时 - 如果5秒后录音未启动，则重置连接
      setTimeout(() => {
        if (!isRecordingStarted && btnStatus.value === "OPEN") {
          console.error("录音启动超时");
          showError("录音启动超时，请重试");
          resetConnection();
        }
      }, 5000);
      
    } catch (error) {
      console.error("启动录音时出错:", error);
      showError("启动录音失败，请检查麦克风权限");
      resetConnection();
    }
  };
  
  // 处理消息
  iatWS.onmessage = (e) => {
    console.log("收到消息:", e.data);
    renderResult(e.data);
  };
  
  // 处理错误
  iatWS.onerror = (e) => {
    // 清除连接超时定时器
    clearTimeout(connectionTimeout);
    
    console.error("WebSocket 错误:", e);
    
    // 如果处于录音状态，则提示用户
    if (btnStatus.value === "OPEN" || btnStatus.value === "CONNECTING") {
      if (!willReconnect) {
        showError("连接出错，请重试");
      }
    }
    
    // 不执行重置操作，让onclose事件处理
  };
  
  // 处理连接关闭
  iatWS.onclose = (e) => {
    // 清除连接超时定时器
    clearTimeout(connectionTimeout);
    
    console.log("WebSocket关闭, 代码:", e.code, "原因:", e.reason || "服务器主动关闭或网络断开");
    
    // 尝试自动重连
    if ((e.code === 1006 || e.code === 1005) && // 异常关闭
        btnStatus.value === "OPEN" && // 正在录音
        reconnectCount < MAX_RECONNECT && // 未超过最大重连次数
        !willReconnect) { // 避免多次重连
      
      willReconnect = true;
      reconnectCount++;
      
      console.log(`WebSocket异常关闭，尝试第${reconnectCount}次重连...`);
      
      // 先停止录音
      try {
        recorder.stop();
      } catch (error) {}
      
      // 显示重连提示
      ElNotification({
        title: '提示',
        message: `连接已断开，正在第${reconnectCount}次重连...`,
        type: 'warning',
        duration: 2000
      });
      
      // 延迟重连，避免立即重连导致的问题
      setTimeout(() => {
        connectWebSocket();
      }, 1000);
      
      return;
    }
    
    // 不再尝试重连，结束录音
    recorder.stop();
    changeStatus("CLOSED");
    
    // 如果是因为重连而关闭，不显示结果
    if (!willReconnect) {
      // 识别结束，将结果添加到聊天记录
      if (message.value && message.value.trim()) {
        ChatListy.value.push({
          role: 'user',
          text: message.value,
          time: getCurrentTime(),
        });
        message.value = '';
      } else if (btnStatus.value === "OPEN") {
        // 如果是录音状态下关闭但没有识别结果，显示提示
        if (reconnectCount >= MAX_RECONNECT) {
          // 如果是达到最大重连次数后关闭
          showError("连接多次断开，请检查网络后重试");
        } else if (e.code !== 1000) {
          // 非正常关闭且不是主动关闭
          showError("连接异常关闭，请重试");
        }
      }
    }
  };
}

// 开始录音
function startRecording() {
  if (btnStatus.value !== "UNDEFINED" && btnStatus.value !== "CLOSED") {
    // 当前正在录音，执行停止操作
    stopRecording();
    return;
  }
  
  // 重置录音状态和文本
  message.value = '';
  resultText.value = '';
  resultTextTemp.value = '';
  
  // 先检查麦克风权限
  navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true
    }
  })
    .then(() => {
      // 有权限，可以连接WebSocket
      btnText.value = "连接中...";
      connectWebSocket();
    })
    .catch(err => {
      console.error("麦克风访问错误:", err);
      showError(errorMessages.microphoneAccessDenied);
      btnText.value = "点击开始说话";
      btnStatus.value = "CLOSED";
    });
}

// 停止录音函数
function stopRecording() {
  try {
    console.log("手动停止录音");
    
    // 清除计时器
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    
    // 停止录音
    try {
      recorder.stop();
    } catch (error) {
      console.error("停止录音出错:", error);
    }
    
    // 如果WebSocket连接打开，发送最后一帧并关闭
    if (iatWS) {
      if (iatWS.readyState === 1) { // 确保WebSocket处于OPEN状态
        try {
          iatWS.send(
            JSON.stringify({
              data: {
                status: 2, // 结束帧
                format: "audio/L16;rate=16000",
                encoding: "raw",
                audio: ""
              }
            })
          );
          
          // 给WebSocket一些时间处理最后一帧
          setTimeout(() => {
            closeWebSocketSafely();
          }, 500);
        } catch (error) {
          console.error("停止时发送最后一帧出错:", error);
          closeWebSocketSafely();
        }
      } else {
        closeWebSocketSafely();
      }
    }
    
    // 更新按钮状态
    btnText.value = "点击开始说话";
    btnStatus.value = "CLOSED";
    
    // 提示用户录音已停止
    ElNotification({
      title: '提示',
      message: "录音已停止",
      type: 'info',
      duration: 2000
    });
  } catch (error) {
    console.error("停止录音时出错:", error);
    resetConnection(); // 出错时强制重置
  }
}

// 安全关闭WebSocket连接（新增函数）
function closeWebSocketSafely() {
  if (!iatWS) return;
  
  try {
    if (iatWS.readyState === 0 || iatWS.readyState === 1) {
      iatWS.close();
    }
  } catch (error) {
    console.error("关闭WebSocket时出错:", error);
  } finally {
    iatWS = null;
  }
}

// 重置连接函数
function resetConnection() {
  try {
    closeWebSocketSafely();
    
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    
    try {
      recorder.stop();
    } catch (error) {
      console.error("停止录音时出错:", error);
    }
    
    btnText.value = "点击开始说话";
    btnStatus.value = "CLOSED";
    
    // 清空临时结果
    resultText.value = '';
    resultTextTemp.value = '';
  } catch (error) {
    console.error("重置连接时出错:", error);
  }
}

// 发送消息
function sendMessage() {
  if (!message.value.trim()) return;
  
  // 将用户输入添加到聊天记录
  ChatListy.value.push({
    role: 'user',
    text: message.value,
    time: getCurrentTime(),
  });
  
  // 这里可以添加发送给服务器的请求逻辑
  // 模拟AI回复
  setTimeout(() => {
    ChatListy.value.push({
      role: 'Ai',
      text: "收到您的消息: " + message.value,
      time: getCurrentTime(),
    });
    message.value = '';
  }, 500);
}

// 处理回车键事件
function handleEnter() {
  sendMessage();
}
</script>

<template>
  <div class="voice-container">
    <div class="record-btn-container">
      <el-button type="danger" round @click="startRecording()">{{ btnText }}</el-button>
    </div>
    
    <div class="chat-container">
      <div class="chat-header">语音识别结果</div>
      <div class="chat-messages">
        <div v-for="(item, index) in ChatListy" :key="index" :class="['chat-message', item.role]">
          <div class="message-content">{{ item.text }}</div>
          <div class="message-time">{{ item.time }}</div>
        </div>
      </div>
      <div class="input-box">
        <el-input v-model="message" placeholder="输入文字消息" @keyup.enter="handleEnter" />
        <el-button type="primary" @click="sendMessage">发送</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.voice-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.record-btn-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.chat-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  background-color: #0B51DB;
  color: white;
  padding: 10px;
  text-align: center;
  font-weight: bold;
}

.chat-messages {
  height: 300px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f9f9f9;
}

.chat-message {
  margin-bottom: 10px;
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 8px;
  position: relative;
}

.chat-message.user {
  background-color: #06b6a7;
  color: white;
  align-self: flex-end;
  margin-left: auto;
}

.chat-message.Ai {
  background-color: #e0f2f2;
  color: #06b6a7;
  align-self: flex-start;
}

.message-time {
  font-size: 0.7rem;
  color: #888;
  margin-top: 4px;
  text-align: right;
}

.input-box {
  display: flex;
  padding: 10px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

.input-box .el-input {
  flex: 1;
  margin-right: 10px;
}
</style> 