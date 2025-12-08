import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 180000,  // 3分钟，支持深度思考
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
   * 发送聊天消息
   * @param {string} message - 消息内容
   * @param {string} sessionId - 会话ID
   * @param {boolean} enableWebSearch - 是否启用联网搜索
   * @param {boolean} deepThink - 是否启用深度思考(TOT)
   * @param {number} thoughtBranches - 思考分支数量
   * @param {number} thoughtDepth - 思考深度
   */
  sendMessage: async (message, sessionId = 'default', enableWebSearch = false, deepThink = false, thoughtBranches = 3, thoughtDepth = 2) => {
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
