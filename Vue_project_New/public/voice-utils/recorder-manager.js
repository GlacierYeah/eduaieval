/**
 * 录音管理器加载脚本
 * 用于全局提供RecorderManager类
 */
(function() {
  // 检查是否已加载
  if (window.RecorderManager) {
    console.log('RecorderManager已加载');
    return;
  }
  
  // 加载依赖
  function loadScript(url) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = url;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`加载脚本失败: ${url}`));
      document.head.appendChild(script);
    });
  }
  
  // 异步加载所需脚本
  async function loadDependencies() {
    try {
      // 加载CryptoJS（如果未加载）
      if (!window.CryptoJS) {
        await loadScript('/voice-utils/utilJS/crypto-js.js');
      }
      
      // 加载RecorderManager（如果未加载）
      if (!window.RecorderManager) {
        await loadScript('/voice-utils/utilJS/index.umd.js');
      }
      
      console.log('语音识别依赖加载成功');
    } catch (error) {
      console.error('加载语音识别依赖失败', error);
    }
  }
  
  // 自动加载依赖
  loadDependencies();
})(); 