/**
 * 讯飞语音识别工具类
 * 封装了讯飞API的WebSocket通信和录音处理
 */
export default class VoiceRecognizer {
    constructor(options = {}) {
        // 配置参数
        this.appId = options.appId || "";
        this.apiSecret = options.apiSecret || "";
        this.apiKey = options.apiKey || "";
        this.language = options.language || "zh_cn";
        this.accent = options.accent || "mandarin";

        // 内部状态
        this.recorder = null;
        this.websocket = null;
        this.status = "CLOSED"; // "CLOSED", "CONNECTING", "OPEN", "CLOSING"
        this.resultText = "";
        this.resultTextTemp = "";
        this.reconnectCount = 0;
        this.maxReconnect = options.maxReconnect || 3;
        this.willReconnect = false;

        // 回调函数
        this.onResult = options.onResult || (() => { });
        this.onStart = options.onStart || (() => { });
        this.onStop = options.onStop || (() => { });
        this.onError = options.onError || (() => { });
        this.onStatusChange = options.onStatusChange || (() => { });
    }

    /**
     * 初始化录音管理器
     * @param {string} recorderPath - 录音器工具路径
     */
    initRecorder(recorderPath) {
        try {
            // 确保RecorderManager已加载
            if (typeof RecorderManager === 'undefined') {
                throw new Error("请先加载讯飞语音识别SDK");
            }

            this.recorder = new RecorderManager(recorderPath);
            console.log("录音管理器初始化成功");
            return true;
        } catch (error) {
            console.error("初始化录音管理器失败:", error);
            this.onError("录音管理器初始化失败，请确保已加载讯飞语音识别SDK");
            return false;
        }
    }

    /**
     * 生成WebSocket URL
     * @returns {string} WebSocket连接URL
     */
    getWebSocketUrl() {
        if (!this.appId || !this.apiSecret || !this.apiKey) {
            throw new Error("缺少必要的API凭证参数");
        }

        // 请求地址根据语种不同变化
        const url = "wss://iat-api.xfyun.cn/v2/iat";
        const host = "iat-api.xfyun.cn";

        // 使用正确的当前时间，确保是GMT/UTC时间
        const date = new Date().toUTCString();

        const algorithm = "hmac-sha256";
        const headers = "host date request-line";
        const signatureOrigin = `host: ${host}\ndate: ${date}\nGET /v2/iat HTTP/1.1`;

        // 需要确保CryptoJS已加载
        if (typeof CryptoJS === 'undefined') {
            throw new Error("请先加载CryptoJS");
        }

        const signatureSha = CryptoJS.HmacSHA256(signatureOrigin, this.apiSecret);
        const signature = CryptoJS.enc.Base64.stringify(signatureSha);
        const authorizationOrigin = `api_key="${this.apiKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`;
        const authorization = btoa(authorizationOrigin);

        // 构建URL，确保URL中不包含common和business参数
        return `${url}?authorization=${encodeURIComponent(authorization)}&date=${encodeURIComponent(date)}&host=${host}`;
    }

    /**
     * 音频编码为Base64
     * @param {ArrayBuffer} buffer - 音频数据
     * @returns {string} Base64编码字符串
     */
    toBase64(buffer) {
        try {
            const binary = Array.from(new Uint8Array(buffer))
                .map(byte => String.fromCharCode(byte))
                .join('');
            return window.btoa(binary);
        } catch (e) {
            console.error("音频编码错误:", e);
            return "";
        }
    }

    /**
     * 开始录音识别
     * @returns {Promise} 成功开始识别返回resolve，失败返回reject
     */
    start() {
        return new Promise((resolve, reject) => {
            // 如果正在录音，先停止
            if (this.status !== "CLOSED") {
                this.stop();
            }

            // 重置结果
            this.resultText = "";
            this.resultTextTemp = "";

            // 检查麦克风权限
            navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            })
                .then(() => {
                    try {
                        this._connectWebSocket()
                            .then(() => {
                                this.onStatusChange("OPEN");
                                this.onStart();
                                resolve();
                            })
                            .catch(error => {
                                console.error("WebSocket连接失败:", error);
                                this.onError("连接失败: " + (error.message || "未知错误"));
                                this.onStatusChange("CLOSED");
                                reject(error);
                            });
                    } catch (error) {
                        console.error("启动识别失败:", error);
                        this.onError("启动失败: " + (error.message || "未知错误"));
                        this.onStatusChange("CLOSED");
                        reject(error);
                    }
                })
                .catch(error => {
                    console.error("麦克风访问错误:", error);
                    this.onError("无法访问麦克风，请确保授予麦克风访问权限");
                    this.onStatusChange("CLOSED");
                    reject(error);
                });
        });
    }

    /**
     * 停止录音识别
     */
    stop() {
        console.log("停止录音识别");

        try {
            // 停止录音
            if (this.recorder) {
                this.recorder.stop();
            }

            // 发送结束帧
            if (this.websocket && this.websocket.readyState === 1) {
                try {
                    this.websocket.send(
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
                        this._closeWebSocketSafely();
                    }, 500);
                } catch (error) {
                    console.error("发送结束帧失败:", error);
                    this._closeWebSocketSafely();
                }
            } else {
                this._closeWebSocketSafely();
            }

            this.status = "CLOSED";
            this.onStatusChange("CLOSED");
            this.onStop(this.resultText);
        } catch (error) {
            console.error("停止录音时出错:", error);
            this._resetConnection();
            this.onError("停止录音失败: " + (error.message || "未知错误"));
        }
    }

    /**
     * 建立WebSocket连接
     * @private
     * @returns {Promise} 连接成功返回resolve，失败返回reject
     */
    _connectWebSocket() {
        return new Promise((resolve, reject) => {
            // 先关闭现有连接
            this._closeWebSocketSafely();

            try {
                const websocketUrl = this.getWebSocketUrl();
                this.websocket = new WebSocket(websocketUrl);
                this.status = "CONNECTING";
                this.onStatusChange("CONNECTING");

                // 连接超时定时器
                const connectionTimeout = setTimeout(() => {
                    if (this.status === "CONNECTING") {
                        reject(new Error("连接超时"));
                        this._closeWebSocketSafely();
                    }
                }, 10000);

                this.websocket.onopen = () => {
                    // 清除超时定时器
                    clearTimeout(connectionTimeout);

                    // 重置重连计数
                    this.reconnectCount = 0;
                    this.willReconnect = false;

                    // 检查连接状态
                    if (!this.websocket || this.websocket.readyState !== 1) {
                        reject(new Error("WebSocket连接异常"));
                        return;
                    }

                    this.status = "OPEN";

                    // 发送初始化帧
                    try {
                        const initParams = {
                            common: {
                                app_id: this.appId
                            },
                            business: {
                                language: this.language,
                                domain: "iat",
                                accent: this.accent,
                                vad_eos: 10000,
                                ptt: 0,
                                dwa: "wpgs"
                            },
                            data: {
                                status: 0,
                                format: "audio/L16;rate=16000",
                                encoding: "raw",
                                audio: ""
                            }
                        };

                        this.websocket.send(JSON.stringify(initParams));
                        
                        // 初始化成功，开始设置录音
                        this._setupRecorder();
                        resolve();
                    } catch (error) {
                        console.error("发送初始化帧失败:", error);
                        reject(new Error("初始化失败"));
                        this._resetConnection();
                    }
                };

                this.websocket.onmessage = (e) => {
                    this._handleMessage(e.data);
                };

                this.websocket.onerror = (e) => {
                    console.error("WebSocket错误:", e);
                    clearTimeout(connectionTimeout);

                    if (this.status === "OPEN" || this.status === "CONNECTING") {
                        if (!this.willReconnect) {
                            this.onError("连接错误");
                        }
                    }
                };

                this.websocket.onclose = (e) => {
                    clearTimeout(connectionTimeout);
                    console.log("WebSocket关闭, 代码:", e.code, "原因:", e.reason || "服务器主动关闭或网络断开");

                    // 尝试自动重连
                    if ((e.code === 1006 || e.code === 1005) &&
                        this.status === "OPEN" &&
                        this.reconnectCount < this.maxReconnect &&
                        !this.willReconnect) {

                        this.willReconnect = true;
                        this.reconnectCount++;

                        console.log(`WebSocket异常关闭，尝试第${this.reconnectCount}次重连...`);

                        // 停止录音
                        if (this.recorder) {
                            try {
                                this.recorder.stop();
                            } catch (error) { }
                        }

                        // 延迟重连
                        setTimeout(() => {
                            this._connectWebSocket()
                                .then(resolve)
                                .catch(reject);
                        }, 1000);

                        return;
                    }

                    // 不再尝试重连，结束录音
                    if (this.recorder) {
                        try {
                            this.recorder.stop();
                        } catch (error) { }
                    }
                    
                    this.status = "CLOSED";
                    this.onStatusChange("CLOSED");
                    
                    if (!this.willReconnect) {
                        // 如果是录音状态下关闭但没有识别结果
                        if (this.status === "OPEN") {
                            if (this.reconnectCount >= this.maxReconnect) {
                                this.onError("连接多次断开，请检查网络后重试");
                            } else if (e.code !== 1000) {
                                this.onError("连接异常关闭，请重试");
                            }
                        }
                    }
                    
                    if (this.status !== "OPEN") {
                        reject(new Error("连接关闭"));
                    }
                };
            } catch (error) {
                console.error("创建WebSocket连接失败:", error);
                reject(error);
            }
        });
    }

    /**
     * 设置录音器
     * @private
     */
    _setupRecorder() {
        if (!this.recorder) {
            throw new Error("录音管理器未初始化");
        }

        this.recorder.onFrameRecorded = ({ isLastFrame, frameBuffer }) => {
            // 检查WebSocket状态
            if (!this.websocket || this.websocket.readyState !== 1) {
                console.log("WebSocket已关闭，丢弃音频帧");
                return;
            }

            if (this.status === "OPEN" && this.websocket.readyState === 1) {
                // 最后一帧为空，结束
                if (isLastFrame && !frameBuffer) {
                    try {
                        this.websocket.send(
                            JSON.stringify({
                                data: {
                                    status: 2,
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
                    if (frameBuffer && frameBuffer.byteLength > 0) {
                        const audio = this.toBase64(frameBuffer);
                        if (audio) {
                            this.websocket.send(
                                JSON.stringify({
                                    data: {
                                        status: isLastFrame ? 2 : 1,
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

        this.recorder.onStop = () => {
            // 如果录音没有做到最后，发送最后一帧
            if (this.status === "OPEN" && this.websocket && this.websocket.readyState === 1) {
                try {
                    this.websocket.send(
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

        // 启动录音
        try {
            this.recorder.start({
                sampleRate: 16000,
                frameSize: 1280,
                arrayBufferType: "short16"
            }).catch(error => {
                console.error("启动录音失败:", error);
                this.onError("无法访问麦克风，请确保授予麦克风访问权限");
                this._resetConnection();
            });
        } catch (error) {
            console.error("启动录音时出错:", error);
            this.onError("启动录音失败，请检查麦克风权限");
            this._resetConnection();
            throw error;
        }
    }

    /**
     * 处理WebSocket消息
     * @private
     * @param {string} data - 收到的消息数据
     */
    _handleMessage(data) {
        try {
            const jsonData = JSON.parse(data);

            // 检查错误码
            if (jsonData.code !== 0) {
                console.error(`讯飞API错误: 代码 ${jsonData.code}, 消息: ${jsonData.message}, 会话ID: ${jsonData.sid}`);

                // 特定错误处理
                if (jsonData.code === 10165) {
                    this.onError("会话ID无效，正在重新连接...");
                    // 清理现有连接
                    this._resetConnection();

                    // 延迟2秒后重新尝试连接
                    setTimeout(() => {
                        this.start().catch(error => {
                            console.error("重新连接失败:", error);
                        });
                    }, 2000);
                } else {
                    this.onError(`识别错误(${jsonData.code}): ${jsonData.message || "识别出错，请重试"}`);
                }

                if (this.websocket && this.websocket.readyState === 1) {
                    this.websocket.close();
                }
                return;
            }

            // 处理识别结果
            if (jsonData.data && jsonData.data.result) {
                let data = jsonData.data.result;
                let str = "";

                // 确保ws字段存在且有内容
                if (data.ws && data.ws.length > 0) {
                    for (let i = 0; i < data.ws.length; i++) {
                        // 确保cw字段存在且有内容
                        if (data.ws[i].cw && data.ws[i].cw.length > 0) {
                            let word = data.ws[i].cw[0].w;
                            if (word && word.trim() !== "") {
                                str += word;
                            }
                        }
                    }

                    // 检查是否有内容
                    if (str.trim() !== "") {
                        console.log("识别到文字:", str);

                        // 开启wpgs会有此字段(前提：在控制台开通动态修正功能)
                        if (data.pgs) {
                            if (data.pgs === "apd") {
                                // 将resultTextTemp同步给resultText
                                this.resultText = this.resultTextTemp;
                            }
                            // 将结果存储在resultTextTemp中
                            this.resultTextTemp = this.resultText + str;
                            
                            // 回调临时结果
                            this.onResult(this.resultTextTemp, false);
                        } else {
                            this.resultText = this.resultText + str;
                            // 回调最终结果
                            this.onResult(this.resultText, true);
                        }
                    }
                }
            }

            // 会话结束
            if (jsonData.code === 0 && jsonData.data && jsonData.data.status === 2) {
                console.log("会话结束，当前识别文本:", this.resultText);

                // 检查最终是否有识别结果
                if (!this.resultText || this.resultText.trim() === "") {
                    this.onError("未能识别到语音，请靠近麦克风并重试");
                }

                if (this.websocket) {
                    this.websocket.close();
                }
            }
        } catch (error) {
            console.error("解析结果时出错:", error);
        }
    }

    /**
     * 安全关闭WebSocket连接
     * @private
     */
    _closeWebSocketSafely() {
        if (!this.websocket) return;

        try {
            if (this.websocket.readyState === 0 || this.websocket.readyState === 1) {
                this.websocket.close();
            }
        } catch (error) {
            console.error("关闭WebSocket时出错:", error);
        } finally {
            this.websocket = null;
        }
    }

    /**
     * 重置连接
     * @private
     */
    _resetConnection() {
        try {
            this._closeWebSocketSafely();

            if (this.recorder) {
                try {
                    this.recorder.stop();
                } catch (error) {
                    console.error("停止录音时出错:", error);
                }
            }

            this.status = "CLOSED";
            this.onStatusChange("CLOSED");

            // 清空临时结果
            this.resultText = '';
            this.resultTextTemp = '';
        } catch (error) {
            console.error("重置连接时出错:", error);
        }
    }
} 