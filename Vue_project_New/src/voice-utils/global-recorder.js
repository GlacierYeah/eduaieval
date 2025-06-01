/**
 * 全局语音识别工具加载脚本
 * 将RecorderManager暴露为全局变量
 */

// 动态加载脚本而不是使用ES模块导入
function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = url;
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

// 获取基础路径
function getBasePath() {
  const isDev = window.location.port === '5173' || window.location.port === '5174';
  return isDev ? '/src/voice-utils' : '/voice-utils';
}

// 初始化加载
async function initRecorderManager() {
  try {
    console.log('开始加载语音识别工具...');
    const basePath = getBasePath();
    console.log('使用路径:', basePath);
    
    // 先加载CryptoJS
    await loadScript(`${basePath}/utilJS/crypto-js.js`);
    console.log('CryptoJS加载成功');
    
    // 然后加载RecorderManager
    await loadScript(`${basePath}/utilJS/index.umd.js`);
    console.log('RecorderManager加载成功');
    
    // 检查是否已全局注册
    if (typeof window.RecorderManager === 'undefined') {
      console.error('RecorderManager未在全局范围注册');
    } else {
      console.log('RecorderManager已成功注册为全局变量');
    }
  } catch (error) {
    console.error('加载语音识别工具失败:', error);
  }
}

// 执行初始化
if (typeof window !== 'undefined') {
  // 如果已经加载过，则跳过
  if (typeof window.RecorderManager === 'undefined') {
    initRecorderManager();
  } else {
    console.log('RecorderManager已经存在，跳过加载');
  }
}

// 导出一个空对象，因为我们不能导出未加载的RecorderManager
export default {}; 