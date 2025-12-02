<template>
  <div class="app-container">
    <!-- 登录/注册页面 -->
    <div v-if="!isLoggedIn" class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <svg class="auth-logo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <h1>智能对话助手</h1>
          <p>{{ isLoginMode ? '登录您的账户' : '创建新账户' }}</p>
        </div>
        
        <form @submit.prevent="isLoginMode ? handleLogin() : handleRegister()" class="auth-form">
          <div class="form-group">
            <label>用户名</label>
            <input
              type="text"
              v-model="authForm.username"
              placeholder="请输入用户名"
              required
              minlength="3"
            />
          </div>
          
          <div class="form-group" v-if="!isLoginMode">
            <label>邮箱（可选）</label>
            <input
              type="email"
              v-model="authForm.email"
              placeholder="请输入邮箱"
            />
          </div>
          
          <div class="form-group" v-if="!isLoginMode">
            <label>昵称（可选）</label>
            <input
              type="text"
              v-model="authForm.nickname"
              placeholder="请输入昵称"
            />
          </div>
          
          <div class="form-group">
            <label>密码</label>
            <input
              type="password"
              v-model="authForm.password"
              placeholder="请输入密码"
              required
              minlength="6"
            />
          </div>
          
          <button type="submit" class="btn btn-primary" :disabled="authLoading">
            {{ authLoading ? '处理中...' : (isLoginMode ? '登录' : '注册') }}
          </button>
        </form>
        
        <div class="auth-switch">
          <span>{{ isLoginMode ? '还没有账户？' : '已有账户？' }}</span>
          <a href="#" @click.prevent="toggleAuthMode">
            {{ isLoginMode ? '立即注册' : '立即登录' }}
          </a>
        </div>
      </div>
    </div>

    <!-- 主界面 -->
    <template v-else>
      <!-- 头部 -->
      <header class="header">
        <div class="header-content">
          <div class="logo">
            <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <h1>智能对话助手</h1>
          </div>
          <div class="header-actions">
            <span class="user-info">{{ user?.nickname || user?.username }}</span>
            <button class="btn btn-ghost" @click="openHistory" title="历史记录">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </button>
            <button class="btn btn-ghost" @click="showStats" title="查看统计">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 20V10M12 20V4M6 20v-6"></path>
              </svg>
            </button>
            <button class="btn btn-ghost" @click="showSettings = true" title="设置">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
              </svg>
            </button>
            <button class="btn btn-ghost" @click="handleLogout" title="退出登录">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="main-content">
        <div class="chat-container">
          <!-- 消息列表 -->
          <div class="messages-wrapper" ref="messagesWrapper">
            <div class="messages">
              <!-- 欢迎消息 -->
              <div v-if="messages.length === 0" class="welcome-message fade-in">
                <div class="welcome-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                </div>
                <h2>你好，{{ user?.nickname || user?.username }}！</h2>
                <p>我是你的智能对话助手，具有长时记忆能力。</p>
                <div class="welcome-tips">
                  <div class="tip">💬 试着告诉我你的名字</div>
                  <div class="tip">🧠 我会记住你分享的信息</div>
                  <div class="tip">🔍 随时可以问我之前聊过的话题</div>
                </div>
              </div>

              <!-- 消息气泡 -->
              <div
                v-for="(msg, index) in messages"
                :key="index"
                :class="['message', msg.role, 'fade-in']"
              >
                <div class="message-avatar">
                  <svg v-if="msg.role === 'user'" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                </div>
                <div class="message-content">
                  <div class="message-bubble" v-html="formatMessage(msg.content)"></div>
                  <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
                </div>
              </div>

              <!-- 加载中 -->
              <div v-if="isLoading" class="message assistant fade-in">
                <div class="message-avatar">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                </div>
                <div class="message-content">
                  <div class="message-bubble typing">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="input-container">
              <textarea
                ref="inputField"
                v-model="inputMessage"
                @keydown.enter.exact.prevent="sendMessage"
                placeholder="输入消息..."
                rows="1"
                :disabled="isLoading"
              ></textarea>
              <button
                class="send-btn"
                @click="sendMessage"
                :disabled="!inputMessage.trim() || isLoading"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </main>

      <!-- 历史记录弹窗 -->
      <div v-if="showHistory" class="modal-overlay" @click.self="showHistory = false">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h3>对话历史</h3>
            <button class="close-btn" @click="showHistory = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="historyLoading" class="loading-text">加载中...</div>
            <div v-else-if="chatHistory.length === 0" class="empty-text">暂无对话历史</div>
            <div v-else class="history-list">
              <div
                v-for="item in chatHistory"
                :key="item.id"
                class="history-item"
              >
                <div class="history-user">
                  <span class="history-label">你：</span>
                  {{ item.userMessage }}
                </div>
                <div class="history-assistant">
                  <span class="history-label">助手：</span>
                  {{ item.assistantResponse }}
                </div>
                <div class="history-time">{{ formatDateTime(item.createdAt) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设置弹窗 -->
      <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
        <div class="modal">
          <div class="modal-header">
            <h3>设置</h3>
            <button class="close-btn" @click="showSettings = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="setting-group">
              <h4>记忆管理</h4>
              <button class="btn btn-outline" @click="clearShortTermMemory">
                清除当前会话记忆
              </button>
              <button class="btn btn-danger" @click="clearAllMemory">
                清除所有记忆
              </button>
            </div>
            <div class="setting-group">
              <h4>历史记录</h4>
              <button class="btn btn-danger" @click="deleteAllHistory">
                删除所有对话历史
              </button>
            </div>
            <div class="setting-group">
              <h4>记忆统计</h4>
              <div class="stats-display" v-if="stats">
                <div class="stat-item">
                  <span class="stat-label">长时记忆</span>
                  <span class="stat-value">{{ stats.longTermMemories }} 条</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">短时记忆</span>
                  <span class="stat-value">{{ stats.shortTermMessages }} 条</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Toast 提示 -->
      <div v-if="toast.show" :class="['toast', toast.type]">
        {{ toast.message }}
      </div>
    </template>
  </div>
</template>

<script>
import { ref, nextTick, onMounted, computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { authApi, chatApi, historyApi } from './api/chat';

export default {
  name: 'App',
  setup() {
    // 认证相关
    const isLoginMode = ref(true);
    const authLoading = ref(false);
    const authForm = ref({
      username: '',
      password: '',
      email: '',
      nickname: '',
    });
    const user = ref(null);
    const token = ref(localStorage.getItem('token'));
    
    const isLoggedIn = computed(() => !!token.value);
    
    // 聊天相关
    const messages = ref([]);
    const inputMessage = ref('');
    const isLoading = ref(false);
    const showSettings = ref(false);
    const showHistory = ref(false);
    const stats = ref(null);
    const messagesWrapper = ref(null);
    const inputField = ref(null);
    const toast = ref({ show: false, message: '', type: 'info' });
    
    // 历史记录
    const chatHistory = ref([]);
    const historyLoading = ref(false);

    // 配置 marked
    marked.setOptions({
      breaks: true,
      gfm: true,
    });

    // 格式化消息（支持 Markdown）
    const formatMessage = (content) => {
      const html = marked.parse(content);
      return DOMPurify.sanitize(html);
    };

    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
      });
    };
    
    // 格式化日期时间
    const formatDateTime = (timestamp) => {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN');
    };

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesWrapper.value) {
          messagesWrapper.value.scrollTop = messagesWrapper.value.scrollHeight;
        }
      });
    };

    // 显示提示
    const showToast = (message, type = 'info') => {
      toast.value = { show: true, message, type };
      setTimeout(() => {
        toast.value.show = false;
      }, 3000);
    };

    // 切换登录/注册模式
    const toggleAuthMode = () => {
      isLoginMode.value = !isLoginMode.value;
      authForm.value = {
        username: '',
        password: '',
        email: '',
        nickname: '',
      };
    };

    // 处理登录
    const handleLogin = async () => {
      authLoading.value = true;
      try {
        const response = await authApi.login(
          authForm.value.username,
          authForm.value.password
        );
        if (response.success && response.data) {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data));
          token.value = response.data.token;
          user.value = response.data;
          showToast('登录成功', 'success');
        } else {
          showToast(response.message || '登录失败', 'error');
        }
      } catch (error) {
        showToast('用户名或密码错误', 'error');
      } finally {
        authLoading.value = false;
      }
    };

    // 处理注册
    const handleRegister = async () => {
      authLoading.value = true;
      try {
        const response = await authApi.register(
          authForm.value.username,
          authForm.value.password,
          authForm.value.email,
          authForm.value.nickname
        );
        if (response.success && response.data) {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data));
          token.value = response.data.token;
          user.value = response.data;
          showToast('注册成功', 'success');
        } else {
          showToast(response.message || '注册失败', 'error');
        }
      } catch (error) {
        showToast(error.response?.data?.message || '注册失败', 'error');
      } finally {
        authLoading.value = false;
      }
    };

    // 退出登录
    const handleLogout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      token.value = null;
      user.value = null;
      messages.value = [];
      showToast('已退出登录', 'info');
    };

    // 发送消息
    const sendMessage = async () => {
      const content = inputMessage.value.trim();
      if (!content || isLoading.value) return;

      // 添加用户消息
      messages.value.push({
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      });
      inputMessage.value = '';
      isLoading.value = true;
      scrollToBottom();

      try {
        const response = await chatApi.sendMessage(content);
        if (response.success && response.data) {
          messages.value.push({
            role: 'assistant',
            content: response.data.message,
            timestamp: new Date().toISOString(),
          });
        } else {
          showToast(response.message || '发送失败', 'error');
        }
      } catch (error) {
        console.error('Send message error:', error);
        showToast('发送失败，请检查网络连接', 'error');
      } finally {
        isLoading.value = false;
        scrollToBottom();
      }
    };

    // 显示统计
    const showStats = async () => {
      try {
        const response = await chatApi.getStats();
        if (response.success && response.data) {
          stats.value = response.data;
          showSettings.value = true;
        }
      } catch (error) {
        showToast('获取统计信息失败', 'error');
      }
    };

    // 加载历史记录
    const loadHistory = async () => {
      historyLoading.value = true;
      try {
        const response = await historyApi.getChatHistory();
        if (response.success && response.data) {
          chatHistory.value = response.data;
        }
      } catch (error) {
        showToast('加载历史记录失败', 'error');
      } finally {
        historyLoading.value = false;
      }
    };

    // 清除短期记忆
    const clearShortTermMemory = async () => {
      try {
        const response = await chatApi.clearShortTermMemory();
        if (response.success) {
          showToast('会话记忆已清除', 'success');
          await showStats();
        }
      } catch (error) {
        showToast('清除失败', 'error');
      }
    };

    // 清除所有记忆
    const clearAllMemory = async () => {
      if (!confirm('确定要清除所有记忆吗？此操作不可恢复。')) return;

      try {
        const response = await chatApi.clearAllMemory();
        if (response.success) {
          messages.value = [];
          showToast('所有记忆已清除', 'success');
          await showStats();
        }
      } catch (error) {
        showToast('清除失败', 'error');
      }
    };

    // 删除所有历史
    const deleteAllHistory = async () => {
      if (!confirm('确定要删除所有对话历史吗？此操作不可恢复。')) return;

      try {
        const response = await historyApi.deleteAllHistory();
        if (response.success) {
          chatHistory.value = [];
          showToast('所有对话历史已删除', 'success');
        }
      } catch (error) {
        showToast('删除失败', 'error');
      }
    };

    // 监听 showHistory 变化
    const watchShowHistory = () => {
      if (showHistory.value) {
        loadHistory();
      }
    };

    // 初始化
    onMounted(async () => {
      // 恢复用户信息
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        user.value = JSON.parse(savedUser);
      }
    });

    // 监听 showHistory 变化加载历史记录
    const openHistory = () => {
      showHistory.value = true;
      loadHistory();
    };

    return {
      // 认证
      isLoginMode,
      authLoading,
      authForm,
      user,
      isLoggedIn,
      toggleAuthMode,
      handleLogin,
      handleRegister,
      handleLogout,
      // 聊天
      messages,
      inputMessage,
      isLoading,
      showSettings,
      showHistory,
      stats,
      messagesWrapper,
      inputField,
      toast,
      chatHistory,
      historyLoading,
      formatMessage,
      formatTime,
      formatDateTime,
      sendMessage,
      showStats,
      clearShortTermMemory,
      clearAllMemory,
      deleteAllHistory,
      openHistory,
    };
  },
};
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 头部 */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-color);
}

.logo h1 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 按钮 */
.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  padding: 8px;
}

.btn-ghost:hover {
  background: var(--border-color);
  color: var(--text-color);
}

.btn-ghost svg {
  width: 20px;
  height: 20px;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.btn-outline:hover {
  background: var(--bg-color);
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

/* 主内容 */
.main-content {
  flex: 1;
  padding-top: 60px;
  display: flex;
  justify-content: center;
}

.chat-container {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
}

/* 消息区域 */
.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-icon svg {
  width: 40px;
  height: 40px;
  color: white;
}

.welcome-message h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.welcome-message p {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 30px;
}

.welcome-tips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.tip {
  background: rgba(255, 255, 255, 0.15);
  padding: 10px 16px;
  border-radius: 20px;
  font-size: 14px;
}

/* 消息样式 */
.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: var(--user-bubble);
  color: white;
}

.message.assistant .message-avatar {
  background: white;
  color: var(--primary-color);
}

.message-avatar svg {
  width: 20px;
  height: 20px;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.5;
}

.message.user .message-bubble {
  background: var(--user-bubble);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
  background: white;
  color: var(--text-color);
  border-bottom-left-radius: 4px;
  box-shadow: var(--shadow);
}

.message-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  padding: 0 4px;
}

/* 打字动画 */
.typing {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
}

.typing .dot {
  width: 8px;
  height: 8px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: typing 1.4s ease-in-out infinite;
}

.typing .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

/* 输入区域 */
.input-area {
  padding: 16px 20px 24px;
  background: transparent;
}

.input-container {
  display: flex;
  gap: 12px;
  background: white;
  border-radius: 24px;
  padding: 8px 8px 8px 20px;
  box-shadow: var(--shadow-lg);
}

.input-container textarea {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  resize: none;
  max-height: 120px;
  line-height: 1.5;
  padding: 8px 0;
  font-family: inherit;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: var(--primary-color);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 20px;
  height: 20px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-muted);
  border-radius: 8px;
}

.close-btn:hover {
  background: var(--bg-color);
}

.modal-body {
  padding: 20px;
}

.setting-group {
  margin-bottom: 24px;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-group h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.setting-group .btn {
  width: 100%;
  margin-bottom: 8px;
}

.stats-display {
  background: var(--bg-color);
  border-radius: 12px;
  padding: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.stat-item:not(:last-child) {
  border-bottom: 1px solid var(--border-color);
}

.stat-label {
  color: var(--text-muted);
}

.stat-value {
  font-weight: 600;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  color: white;
  z-index: 300;
  animation: slideUp 0.3s ease-out;
}

.toast.info {
  background: #3b82f6;
}

.toast.success {
  background: #10b981;
}

.toast.error {
  background: #ef4444;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .message {
    max-width: 90%;
  }

  .welcome-tips {
    flex-direction: column;
  }

  .tip {
    width: 100%;
    text-align: center;
  }
}
</style>
