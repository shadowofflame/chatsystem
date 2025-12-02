import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 60000,
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
   */
  sendMessage: async (message, sessionId = 'default') => {
    const response = await apiClient.post('/chat', {
      message,
      sessionId,
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
   * 删除所有历史
   */
  deleteAllHistory: async () => {
    const response = await apiClient.delete('/history/all');
    return response;
  },
};

export default { authApi, chatApi, historyApi };
