import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 300000,  // 5分钟，支持深度思考
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Token 过期或无效，清除登录状态
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
    }
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// 认证 API
export const authApi = {
  /**
   * 用户注册
   */
  register: async (username, password, email, nickname) => {
    const response = await apiClient.post('/auth/register', {
      username,
      password,
      email,
      nickname,
    });
    return response;
  },

  /**
   * 用户登录
   */
  login: async (username, password) => {
    const response = await apiClient.post('/auth/login', {
      username,
      password,
    });
    return response;
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response;
  },
};

// 聊天 API
export const chatApi = {
  /**
   * 发送聊天消息（非流式）
   * @param {string} message - 消息内容
   * @param {string} sessionId - 会话ID
   * @param {boolean} enableWebSearch - 是否启用联网搜索
   * @param {boolean} deepThink - 是否启用深度思考(TOT)
   * @param {number} thoughtBranches - 思考分支数量
   * @param {number} thoughtDepth - 思考深度
   */
  sendMessage: async (message, sessionId = 'default', enableWebSearch = false, deepThink = false, thoughtBranches = 5, thoughtDepth = 3) => {
    const response = await apiClient.post('/chat', {
      message,
      sessionId,
      enableWebSearch,
      deepThink,
      thoughtBranches,
      thoughtDepth,
    });
    return response;
  },

  /**
   * 流式发送聊天消息 (SSE)
   * @param {string} message - 消息内容
   * @param {string} sessionId - 会话ID
   * @param {boolean} enableWebSearch - 是否启用联网搜索
   * @param {boolean} deepThink - 是否启用深度思考(TOT)
   * @param {number} thoughtBranches - 思考分支数量
   * @param {number} thoughtDepth - 思考深度
   * @param {Function} onEvent - 事件回调函数
   * @returns {Promise<void>}
   */
  sendMessageStream: async (message, sessionId = 'default', enableWebSearch = false, deepThink = false, thoughtBranches = 5, thoughtDepth = 3, onEvent) => {
    const token = localStorage.getItem('token');
    
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify({
        message,
        sessionId,
        enableWebSearch,
        deepThink,
        thoughtBranches,
        thoughtDepth,
      }),
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    console.log('SSE stream started');  // 调试

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('SSE stream ended');  // 调试
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      console.log('Raw chunk received:', chunk);  // 调试：查看原始数据
      buffer += chunk;
      
      // 解析 SSE 数据
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // 保留不完整的行
      
      for (const line of lines) {
        // 处理可能的双重 data: 前缀 (后端透传 Agent 数据导致)
        let processedLine = line;
        // 移除重复的 data: 前缀
        while (processedLine.startsWith('data:data:')) {
          processedLine = 'data:' + processedLine.slice(10);
        }
        
        if (processedLine.startsWith('data: ') || processedLine.startsWith('data:')) {
          // 提取 JSON 数据部分
          let data = processedLine.startsWith('data: ') 
            ? processedLine.slice(6).trim() 
            : processedLine.slice(5).trim();
          
          if (data) {
            try {
              const event = JSON.parse(data);
              console.log('Parsed event:', event);  // 调试
              if (onEvent) {
                onEvent(event);
              }
            } catch (e) {
              // 可能是空行或非 JSON 数据，忽略
              if (data.length > 0 && !data.startsWith('data:')) {
                console.warn('Failed to parse SSE event:', data, e);
              }
            }
          }
        }
      }
    }
  },

  /**
   * 获取记忆统计
   */
  getStats: async () => {
    const response = await apiClient.get('/chat/stats');
    return response;
  },

  /**
   * 清除短期记忆
   */
  clearShortTermMemory: async () => {
    const response = await apiClient.post('/chat/memory/clear-short-term');
    return response;
  },

  /**
   * 清除所有记忆
   */
  clearAllMemory: async () => {
    const response = await apiClient.post('/chat/memory/clear-all');
    return response;
  },

  /**
   * 健康检查
   */
  healthCheck: async () => {
    const response = await apiClient.get('/chat/health');
    return response;
  },
};

// 历史记录 API
export const historyApi = {
  /**
   * 获取对话历史
   */
  getChatHistory: async () => {
    const response = await apiClient.get('/history');
    return response;
  },

  /**
   * 分页获取对话历史
   */
  getChatHistoryPaged: async (page = 0, size = 20) => {
    const response = await apiClient.get('/history/paged', {
      params: { page, size },
    });
    return response;
  },

  /**
   * 获取指定会话的历史
   */
  getSessionHistory: async (sessionId) => {
    const response = await apiClient.get(`/history/session/${sessionId}`);
    return response;
  },

  /**
   * 获取会话列表
   */
  getSessions: async () => {
    const response = await apiClient.get('/history/sessions');
    return response;
  },

  /**
   * 获取对话数量
   */
  getChatCount: async () => {
    const response = await apiClient.get('/history/count');
    return response;
  },

  /**
   * 删除指定会话
   */
  deleteSession: async (sessionId) => {
    const response = await apiClient.delete(`/history/session/${sessionId}`);
    return response;
  },

  /**
   * 获取指定会话的统计信息
   */
  getSessionStats: async (sessionId) => {
    const response = await apiClient.get(`/history/session/${sessionId}/stats`);
    return response;
  },

  /**
   * 删除所有历史
   */
  deleteAllHistory: async () => {
    const response = await apiClient.delete('/history/all');
    return response;
  },
};

// 文件 API
export const fileApi = {
  /**
   * 上传文件
   * @param {File} file - 要上传的文件
   */
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('token');
    const response = await fetch('/api/files/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    
    return response.json();
  },

  /**
   * 分析文件
   * @param {string} filepath - 文件路径
   * @param {string} question - 关于文件的问题
   */
  analyzeFile: async (filepath, question = '请分析这个文件的内容') => {
    const response = await apiClient.post('/files/analyze', {
      filepath,
      question,
    });
    return response;
  },

  /**
   * 列出已上传的文件
   */
  listFiles: async () => {
    const response = await apiClient.get('/files/list');
    return response;
  },
};

// 充值 API
export const rechargeApi = {
  /**
   * 创建充值订单
   */
  createOrder: async (amount) => {
    const response = await apiClient.post('/recharge/create', { amount });
    return response;
  },

  /**
   * 确认支付
   */
  confirmPayment: async (orderNo) => {
    const response = await apiClient.post(`/recharge/confirm/${orderNo}`);
    return response;
  },

  /**
   * 取消订单
   */
  cancelOrder: async (orderNo) => {
    const response = await apiClient.post(`/recharge/cancel/${orderNo}`);
    return response;
  },

  /**
   * 获取用户余额
   */
  getBalance: async () => {
    const response = await apiClient.get('/recharge/balance');
    return response;
  },

  /**
   * 获取充值订单列表
   */
  getOrders: async () => {
    const response = await apiClient.get('/recharge/orders');
    return response;
  },

  /**
   * 获取当前待支付订单
   */
  getPendingOrder: async () => {
    const response = await apiClient.get('/recharge/pending');
    return response;
  },

  /**
   * 获取过期订单通知
   */
  getExpiredNotifications: async () => {
    const response = await apiClient.get('/recharge/expired-notifications');
    return response;
  },
};

// 模型 API
export const modelApi = {
  /**
   * 获取所有可用模型
   */
  getModels: async () => {
    const response = await apiClient.get('/models');
    return response;
  },

  /**
   * 获取启用的模型
   */
  getEnabledModels: async () => {
    const response = await apiClient.get('/models/enabled');
    return response;
  },

  /**
   * 获取指定模型详情
   */
  getModelByName: async (modelName) => {
    const response = await apiClient.get(`/models/${modelName}`);
    return response;
  },
};

export default { authApi, chatApi, historyApi, fileApi, rechargeApi, modelApi };
