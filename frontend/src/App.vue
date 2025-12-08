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
            <span class="user-balance" @click="openRecharge" title="点击充值">
              💰 ¥{{ userBalance.toFixed(2) }}
            </span>
            <span class="user-info">{{ user?.nickname || user?.username }}</span>
            <button class="btn btn-ghost" @click="openModelsModal" title="可用模型">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
            </button>
            <button class="btn btn-ghost" @click="openRecharge" title="充值">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                <line x1="1" y1="10" x2="23" y2="10"></line>
              </svg>
            </button>
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
        <!-- 左侧会话列表 -->
        <aside class="sidebar">
          <div class="sidebar-header">
            <h3>会话列表</h3>
            <button class="btn btn-primary btn-sm" @click="createNewSession" title="新建会话">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
          </div>
          <div class="sessions-list">
            <div v-if="sessionsLoading" class="loading-text">加载中...</div>
            <div v-else-if="sessions.length === 0" class="empty-text">暂无会话</div>
            <div
              v-else
              v-for="session in sessions"
              :key="session.sessionId"
              :class="['session-item', { active: session.sessionId === currentSessionId }]"
              @click="switchSession(session.sessionId)"
            >
              <div class="session-info">
                <div class="session-name">{{ session.title || `会话 ${session.sessionId.substring(0, 8)}` }}</div>
                <div class="session-time">{{ formatDateTime(session.lastMessageTime) }}</div>
              </div>
              <div class="session-actions">
                <button 
                  class="session-stats-btn" 
                  @click.stop="showSessionStats(session.sessionId)"
                  title="查看统计"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 20V10M12 20V4M6 20v-6"></path>
                  </svg>
                </button>
                <button 
                  class="session-delete" 
                  @click.stop="deleteSessionConfirm(session.sessionId)"
                  title="删除会话"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </aside>

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
                  <div class="message-meta">
                    <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                    <span v-if="msg.role === 'assistant' && msg.cost !== undefined && msg.cost !== null" class="message-cost" :title="`输入: ${msg.inputCharCount}字, 输出: ${msg.outputCharCount}字, 总计: ${msg.totalCharCount}字`">
                      💰 ¥{{ parseFloat(msg.cost).toFixed(2) }}
                    </span>
                  </div>
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
            <!-- 功能开关 -->
            <div class="input-options">
              <label class="toggle-switch" title="启用联网搜索获取最新信息">
                <input type="checkbox" v-model="enableWebSearch">
                <span class="toggle-slider"></span>
                <span class="toggle-label">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                  </svg>
                  联网搜索
                </span>
              </label>
              <label class="toggle-switch" title="启用深度思考(TOT)进行多分支推理">
                <input type="checkbox" v-model="deepThink">
                <span class="toggle-slider deep-think-slider"></span>
                <span class="toggle-label">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"></path>
                  </svg>
                  深度思考
                </span>
              </label>
            </div>
            
            <!-- 已上传文件显示 -->
            <div v-if="uploadedFile" class="uploaded-file-preview">
              <div class="file-info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span class="file-name">{{ uploadedFile.name }}</span>
                <span class="file-size">({{ formatFileSize(uploadedFile.size) }})</span>
              </div>
              <button class="remove-file-btn" @click="removeUploadedFile" title="移除文件">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            
            <div class="input-container">
              <!-- 文件上传按钮 -->
              <input 
                type="file" 
                ref="fileInput" 
                @change="handleFileSelect" 
                style="display: none"
                accept=".txt,.pdf,.doc,.docx,.md,.json,.csv,.py,.java,.js,.ts,.html,.css,.xml,.yaml,.yml"
              >
              <button 
                class="upload-btn" 
                @click="$refs.fileInput.click()" 
                :disabled="isLoading || isUploading"
                title="上传文件"
              >
                <svg v-if="!isUploading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                </svg>
                <span v-else class="upload-spinner"></span>
              </button>
              
              <textarea
                ref="inputField"
                v-model="inputMessage"
                @keydown.enter.exact.prevent="sendMessage"
                :placeholder="getInputPlaceholder()"
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
                <div class="history-meta">
                  <span class="history-time">{{ formatDateTime(item.createdAt) }}</span>
                  <span v-if="item.cost !== undefined && item.cost !== null" class="history-cost" :title="`输入: ${item.inputCharCount}字, 输出: ${item.outputCharCount}字, 总计: ${item.totalCharCount}字`">
                    💰 ¥{{ parseFloat(item.cost).toFixed(2) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 可用模型列表弹窗 -->
      <div v-if="showModelsModal" class="modal-overlay" @click.self="showModelsModal = false">
        <div class="modal modal-models">
          <div class="modal-header">
            <h3>🤖 可用模型</h3>
            <button class="close-btn" @click="showModelsModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="modelsLoading" class="loading-text">加载中...</div>
            <div v-else-if="modelsList.length === 0" class="empty-text">暂无可用模型</div>
            <div v-else class="models-list">
              <div 
                v-for="model in modelsList" 
                :key="model.id" 
                class="model-card"
              >
                <div class="model-header">
                  <div class="model-name">{{ model.displayName }}</div>
                  <div class="model-provider">{{ model.provider }}</div>
                </div>
                <div class="model-price">
                  <span class="price-label">计费标准</span>
                  <span class="price-value">¥{{ parseFloat(model.pricePer10kChars).toFixed(2) }} / 万字</span>
                </div>
                <div class="model-services" v-if="model.serviceCount > 0">
                  <span class="service-count">{{ model.serviceCount }} 次调用</span>
                </div>
                <div class="model-description" v-if="model.serviceDescription">
                  {{ model.serviceDescription }}
                </div>
                <div class="model-features" v-if="model.capabilities && model.capabilities.length > 0">
                  <span 
                    v-for="(capability, idx) in model.capabilities" 
                    :key="idx" 
                    class="feature-tag"
                  >{{ capability }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 会话统计弹窗 -->
      <div v-if="showSessionStatsModal" class="modal-overlay" @click.self="showSessionStatsModal = false">
        <div class="modal">
          <div class="modal-header">
            <h3>📊 会话统计</h3>
            <button class="close-btn" @click="showSessionStatsModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="sessionStatsLoading" class="loading-text">加载中...</div>
            <div v-else class="session-stats-content">
              <div class="stats-section">
                <h4>🤖 使用模型</h4>
                <div class="stats-value model-name">{{ sessionStatsData.model || 'deepseek-chat' }}</div>
              </div>
              <div class="stats-section">
                <h4>📝 字数统计</h4>
                <div class="stats-grid">
                  <div class="stat-box">
                    <div class="stat-label">输入字数</div>
                    <div class="stat-number">{{ sessionStatsData.inputCharCount?.toLocaleString() || 0 }}</div>
                  </div>
                  <div class="stat-box">
                    <div class="stat-label">输出字数</div>
                    <div class="stat-number">{{ sessionStatsData.outputCharCount?.toLocaleString() || 0 }}</div>
                  </div>
                  <div class="stat-box">
                    <div class="stat-label">总字数</div>
                    <div class="stat-number">{{ sessionStatsData.totalCharCount?.toLocaleString() || 0 }}</div>
                  </div>
                  <div class="stat-box">
                    <div class="stat-label">对话次数</div>
                    <div class="stat-number">{{ sessionStatsData.messageCount || 0 }}</div>
                  </div>
                </div>
              </div>
              <div class="stats-section">
                <h4>💰 消费金额</h4>
                <div class="stats-value cost-value">¥{{ parseFloat(sessionStatsData.totalCost || 0).toFixed(2) }}</div>
                <div class="cost-hint">计费规则：每10000字收费1元</div>
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

      <!-- 充值弹窗 -->
      <div v-if="showRecharge" class="modal-overlay" @click.self="closeRecharge">
        <div class="modal modal-recharge">
          <div class="modal-header">
            <h3>💰 账户充值</h3>
            <button class="close-btn" @click="closeRecharge">&times;</button>
          </div>
          <div class="modal-body">
            <!-- 余额显示 -->
            <div class="balance-display">
              <span class="balance-label">当前余额</span>
              <span class="balance-value">¥{{ userBalance.toFixed(2) }}</span>
            </div>

            <!-- 如果有待支付订单 -->
            <div v-if="currentOrder" class="pending-order">
              <div class="order-info">
                <h4>待支付订单</h4>
                <p class="order-no">订单号: {{ currentOrder.orderNo }}</p>
                <p class="order-amount">充值金额: <strong>¥{{ currentOrder.amount }}</strong></p>
                <p class="order-countdown" :class="{ warning: remainingTime < 60 }">
                  剩余支付时间: <strong>{{ formatCountdown(remainingTime) }}</strong>
                </p>
              </div>
              <div class="order-actions">
                <button class="btn btn-primary btn-lg" @click="confirmPayment" :disabled="rechargeLoading">
                  {{ rechargeLoading ? '处理中...' : '确认已支付' }}
                </button>
                <button class="btn btn-ghost" @click="cancelRechargeOrder" :disabled="rechargeLoading">
                  取消订单
                </button>
              </div>
              <p class="payment-note">
                💡 由于本系统为演示版本，点击"确认已支付"即可完成充值
              </p>
            </div>

            <!-- 创建新订单 -->
            <div v-else class="recharge-form">
              <h4>选择充值金额</h4>
              <div class="amount-options">
                <button 
                  v-for="amount in [50, 100, 200]" 
                  :key="amount"
                  :class="['amount-btn', { active: rechargeAmount === amount && !isCustomAmount }]"
                  @click="selectAmount(amount)"
                >
                  ¥{{ amount }}
                </button>
                <button 
                  :class="['amount-btn', { active: isCustomAmount }]"
                  @click="selectCustomAmount"
                >
                  自定义
                </button>
              </div>
              
              <div v-if="isCustomAmount" class="custom-amount">
                <label>输入金额</label>
                <input 
                  type="number" 
                  v-model="customAmount" 
                  placeholder="请输入充值金额（最低1元）"
                  min="1"
                  step="0.01"
                />
              </div>

              <div class="recharge-summary">
                <span>充值金额:</span>
                <strong>¥{{ getRechargeAmount().toFixed(2) }}</strong>
              </div>

              <button 
                class="btn btn-primary btn-lg btn-block" 
                @click="createRechargeOrder"
                :disabled="rechargeLoading || getRechargeAmount() < 1"
              >
                {{ rechargeLoading ? '创建订单中...' : '立即充值' }}
              </button>
              
              <p class="recharge-note">
                ⏰ 订单创建后请在5分钟内完成支付，超时将自动取消
              </p>
            </div>

            <!-- 充值记录链接 -->
            <div class="recharge-history-link">
              <a href="#" @click.prevent="openRechargeHistory">查看充值记录 →</a>
            </div>
          </div>
        </div>
      </div>

      <!-- 充值记录弹窗 -->
      <div v-if="showRechargeHistory" class="modal-overlay" @click.self="showRechargeHistory = false">
        <div class="modal modal-lg">
          <div class="modal-header">
            <h3>充值记录</h3>
            <button class="close-btn" @click="showRechargeHistory = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="rechargeOrders.length === 0" class="empty-text">暂无充值记录</div>
            <div v-else class="recharge-orders-list">
              <div 
                v-for="order in rechargeOrders" 
                :key="order.id" 
                :class="['order-item', order.status.toLowerCase()]"
              >
                <div class="order-left">
                  <div class="order-amount-display">¥{{ order.amount }}</div>
                  <div class="order-time">{{ formatDateTime(order.createdAt) }}</div>
                </div>
                <div class="order-right">
                  <span :class="['order-status', order.status.toLowerCase()]">
                    {{ order.statusText }}
                  </span>
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
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { authApi, chatApi, historyApi, fileApi, rechargeApi, modelApi } from './api/chat';

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
    
    // 会话相关
    const sessions = ref([]);
    const currentSessionId = ref(null);
    const sessionsLoading = ref(false);
    
    // 聊天相关
    const messages = ref([]);
    const inputMessage = ref('');
    const isLoading = ref(false);
    const showSettings = ref(false);
    const showHistory = ref(false);
    const stats = ref(null);
    const messagesWrapper = ref(null);
    const inputField = ref(null);
    const fileInput = ref(null);
    const toast = ref({ show: false, message: '', type: 'info' });
    const enableWebSearch = ref(false);  // 联网搜索开关
    const deepThink = ref(false);  // 深度思考开关(TOT)
    const thoughtBranches = ref(3);  // 思考分支数量
    const thoughtDepth = ref(2);  // 思考深度
    
    // 会话统计相关
    const showSessionStatsModal = ref(false);
    const sessionStatsLoading = ref(false);
    const sessionStatsData = ref({
      model: 'deepseek-chat',
      inputCharCount: 0,
      outputCharCount: 0,
      totalCharCount: 0,
      messageCount: 0,
      totalCost: 0
    });
    
    // 模型列表相关
    const showModelsModal = ref(false);
    const modelsLoading = ref(false);
    const modelsList = ref([]);
    
    // 文件上传相关
    const uploadedFile = ref(null);
    const uploadedFilePath = ref(null);
    const isUploading = ref(false);
    
    // 历史记录
    const chatHistory = ref([]);
    const historyLoading = ref(false);

    // 充值相关
    const showRecharge = ref(false);
    const userBalance = ref(0);
    const rechargeAmount = ref(50);
    const customAmount = ref('');
    const isCustomAmount = ref(false);
    const currentOrder = ref(null);
    const rechargeLoading = ref(false);
    const countdownTimer = ref(null);
    const remainingTime = ref(0);
    const rechargeOrders = ref([]);
    const showRechargeHistory = ref(false);
    const expiredCheckInterval = ref(null);

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
          // 登录成功后加载会话列表
          await loadSessions();
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
          // 注册成功后会话列表为空，不需要特别加载
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
      sessions.value = [];
      currentSessionId.value = null;
      showToast('已退出登录', 'info');
    };

    // 加载会话列表
    const loadSessions = async () => {
      sessionsLoading.value = true;
      try {
        const response = await historyApi.getSessions();
        if (response.success && response.data) {
          // 后端直接返回包含 sessionId、title、lastMessageTime 的对象数组
          sessions.value = response.data.map(session => ({
            sessionId: session.sessionId,
            title: session.title || (session.sessionId === 'default' ? '默认会话' : `会话 ${session.sessionId.substring(0, 8)}`),
            lastMessageTime: session.lastMessageTime
          })).sort((a, b) => new Date(b.lastMessageTime) - new Date(a.lastMessageTime));
          
          // 如果没有当前会话，选择第一个
          if (!currentSessionId.value && sessions.value.length > 0) {
            currentSessionId.value = sessions.value[0].sessionId;
            await loadSessionMessages(currentSessionId.value);
          }
        }
      } catch (error) {
        console.error('加载会话列表失败:', error);
      } finally {
        sessionsLoading.value = false;
      }
    };

    // 加载指定会话的消息
    const loadSessionMessages = async (sessionId) => {
      try {
        const response = await historyApi.getSessionHistory(sessionId);
        if (response.success && response.data) {
          messages.value = response.data.map(item => ([
            {
              role: 'user',
              content: item.userMessage,
              timestamp: item.createdAt
            },
            {
              role: 'assistant',
              content: item.assistantResponse,
              timestamp: item.createdAt
            }
          ])).flat();
          scrollToBottom();
        }
      } catch (error) {
        console.error('加载会话消息失败:', error);
        showToast('加载会话消息失败', 'error');
      }
    };

    // 创建新会话
    const createNewSession = () => {
      const newSessionId = `session_${Date.now()}`;
      currentSessionId.value = newSessionId;
      messages.value = [];
      // 先添加一个临时会话到列表，标题为"新对话"
      sessions.value.unshift({
        sessionId: newSessionId,
        title: '新对话',
        lastMessageTime: new Date().toISOString(),
        isNew: true // 标记为新会话
      });
      showToast('已创建新会话', 'success');
    };

    // 切换会话
    const switchSession = async (sessionId) => {
      if (currentSessionId.value === sessionId) return;
      currentSessionId.value = sessionId;
      await loadSessionMessages(sessionId);
    };

    // 显示会话统计
    const showSessionStats = async (sessionId) => {
      showSessionStatsModal.value = true;
      sessionStatsLoading.value = true;
      
      try {
        const response = await historyApi.getSessionStats(sessionId);
        if (response.success && response.data) {
          sessionStatsData.value = {
            model: response.data.model || 'deepseek-chat',
            inputCharCount: response.data.inputCharCount || 0,
            outputCharCount: response.data.outputCharCount || 0,
            totalCharCount: response.data.totalCharCount || 0,
            messageCount: response.data.messageCount || 0,
            totalCost: response.data.totalCost || 0
          };
        }
      } catch (error) {
        console.error('获取会话统计失败:', error);
        showToast('获取统计信息失败', 'error');
      } finally {
        sessionStatsLoading.value = false;
      }
    };

    // 打开模型列表弹窗
    const openModelsModal = async () => {
      showModelsModal.value = true;
      modelsLoading.value = true;
      
      try {
        const response = await modelApi.getEnabledModels();
        if (response.success && response.data) {
          modelsList.value = response.data;
        }
      } catch (error) {
        console.error('获取模型列表失败:', error);
        showToast('获取模型列表失败', 'error');
      } finally {
        modelsLoading.value = false;
      }
    };

    // 删除会话确认
    const deleteSessionConfirm = async (sessionId) => {
      if (!confirm('确定要删除这个会话吗？此操作不可恢复。')) return;
      
      try {
        const response = await historyApi.deleteSession(sessionId);
        if (response.success) {
          sessions.value = sessions.value.filter(s => s.sessionId !== sessionId);
          
          // 如果删除的是当前会话，切换到其他会话
          if (currentSessionId.value === sessionId) {
            if (sessions.value.length > 0) {
              currentSessionId.value = sessions.value[0].sessionId;
              await loadSessionMessages(currentSessionId.value);
            } else {
              currentSessionId.value = null;
              messages.value = [];
            }
          }
          
          showToast('会话已删除', 'success');
        }
      } catch (error) {
        showToast('删除会话失败', 'error');
      }
    };

    // 文件上传处理
    const handleFileSelect = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      // 检查文件大小（限制 10MB）
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        showToast('文件大小不能超过 10MB', 'error');
        event.target.value = '';
        return;
      }
      
      isUploading.value = true;
      
      try {
        const response = await fileApi.uploadFile(file);
        if (response.success) {
          uploadedFile.value = {
            name: file.name,
            size: file.size,
            type: file.type
          };
          uploadedFilePath.value = response.data.filepath;
          showToast('文件上传成功', 'success');
        } else {
          showToast(response.message || '文件上传失败', 'error');
        }
      } catch (error) {
        console.error('文件上传错误:', error);
        showToast('文件上传失败', 'error');
      } finally {
        isUploading.value = false;
        event.target.value = '';
      }
    };

    // 移除已上传文件
    const removeUploadedFile = () => {
      uploadedFile.value = null;
      uploadedFilePath.value = null;
    };

    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // 获取输入框占位符
    const getInputPlaceholder = () => {
      if (uploadedFile.value) {
        return `已选择文件: ${uploadedFile.value.name}，输入问题...`;
      }
      if (enableWebSearch.value) {
        return '输入消息 (联网搜索已开启)...';
      }
      return '输入消息...';
    };

    // 发送消息
    const sendMessage = async () => {
      const content = inputMessage.value.trim();
      if (!content || isLoading.value) return;

      // 记录当前会话的消息数量，用于判断是否为第一条消息
      const isFirstMessage = messages.value.filter(m => m.role === 'user').length === 0;
      
      // 如果没有当前会话，创建一个
      if (!currentSessionId.value) {
        createNewSession();
      }

      // 构建显示内容和实际发送内容
      let displayContent = content;
      let actualContent = content;
      
      // 如果有上传文件，添加文件信息
      if (uploadedFile.value && uploadedFilePath.value) {
        displayContent = `📎 [${uploadedFile.value.name}] ${content}`;
        actualContent = `请分析文件 ${uploadedFilePath.value} 的内容，然后回答以下问题：${content}`;
      } else if (deepThink.value && enableWebSearch.value) {
        displayContent = `🧠🌐 ${content}`;
      } else if (deepThink.value) {
        displayContent = `🧠 ${content}`;
      } else if (enableWebSearch.value) {
        displayContent = `🌐 ${content}`;
      }
      
      messages.value.push({
        role: 'user',
        content: displayContent,
        timestamp: new Date().toISOString(),
      });
      inputMessage.value = '';
      
      // 清除上传文件状态
      const hadFile = !!uploadedFile.value;
      removeUploadedFile();
      
      isLoading.value = true;
      scrollToBottom();

      try {
        // 发送请求时传入联网搜索参数
        const response = await chatApi.sendMessage(actualContent, currentSessionId.value, enableWebSearch.value, deepThink.value, thoughtBranches.value, thoughtDepth.value);
        if (response.success && response.data) {
          messages.value.push({
            role: 'assistant',
            content: response.data.message,
            timestamp: new Date().toISOString(),
            // 费用相关信息
            cost: response.data.cost,
            inputCharCount: response.data.inputCharCount,
            outputCharCount: response.data.outputCharCount,
            totalCharCount: response.data.totalCharCount,
          });
          
          // 更新余额显示
          if (response.data.newBalance !== null && response.data.newBalance !== undefined) {
            userBalance.value = parseFloat(response.data.newBalance);
          }
          
          // 如果是第一条消息，等待后端生成标题后重新加载会话列表
          if (isFirstMessage) {
            // 延迟一下确保后端已经生成标题
            setTimeout(async () => {
              const sessionsResponse = await historyApi.getSessions();
              if (sessionsResponse.success && sessionsResponse.data) {
                const updatedSession = sessionsResponse.data.find(s => s.sessionId === currentSessionId.value);
                if (updatedSession) {
                  // 找到当前会话并更新标题
                  const sessionIndex = sessions.value.findIndex(s => s.sessionId === currentSessionId.value);
                  if (sessionIndex !== -1) {
                    sessions.value[sessionIndex].title = updatedSession.title;
                    sessions.value[sessionIndex].lastMessageTime = updatedSession.lastMessageTime;
                    delete sessions.value[sessionIndex].isNew;
                  }
                }
              }
            }, 500); // 等待500ms让后端完成标题生成
          } else {
            // 更新会话列表中的最后消息时间
            const session = sessions.value.find(s => s.sessionId === currentSessionId.value);
            if (session) {
              session.lastMessageTime = new Date().toISOString();
              // 重新排序会话列表
              sessions.value.sort((a, b) => new Date(b.lastMessageTime) - new Date(a.lastMessageTime));
            }
          }
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

    // ========== 充值功能 ==========
    
    // 加载用户余额
    const loadBalance = async () => {
      try {
        const response = await rechargeApi.getBalance();
        if (response.success && response.data) {
          userBalance.value = response.data.balance;
        }
      } catch (error) {
        console.error('加载余额失败:', error);
      }
    };

    // 打开充值弹窗
    const openRecharge = async () => {
      showRecharge.value = true;
      rechargeAmount.value = 50;
      isCustomAmount.value = false;
      customAmount.value = '';
      await loadBalance();
      // 检查是否有待支付订单
      await checkPendingOrder();
    };

    // 检查待支付订单
    const checkPendingOrder = async () => {
      try {
        const response = await rechargeApi.getPendingOrder();
        if (response.success && response.data) {
          currentOrder.value = response.data;
          startCountdown(response.data.remainingSeconds);
        }
      } catch (error) {
        console.error('检查待支付订单失败:', error);
      }
    };

    // 选择充值金额
    const selectAmount = (amount) => {
      rechargeAmount.value = amount;
      isCustomAmount.value = false;
      customAmount.value = '';
    };

    // 选择自定义金额
    const selectCustomAmount = () => {
      isCustomAmount.value = true;
      rechargeAmount.value = 0;
    };

    // 获取实际充值金额
    const getRechargeAmount = () => {
      if (isCustomAmount.value) {
        return parseFloat(customAmount.value) || 0;
      }
      return rechargeAmount.value;
    };

    // 创建充值订单
    const createRechargeOrder = async () => {
      const amount = getRechargeAmount();
      if (amount < 1) {
        showToast('充值金额不能小于1元', 'error');
        return;
      }
      
      rechargeLoading.value = true;
      try {
        const response = await rechargeApi.createOrder(amount);
        if (response.success && response.data) {
          currentOrder.value = response.data;
          startCountdown(response.data.remainingSeconds);
          showToast('订单创建成功，请在5分钟内完成支付', 'success');
        } else {
          showToast(response.message || '创建订单失败', 'error');
        }
      } catch (error) {
        showToast('创建订单失败', 'error');
      } finally {
        rechargeLoading.value = false;
      }
    };

    // 确认支付
    const confirmPayment = async () => {
      if (!currentOrder.value) return;
      
      rechargeLoading.value = true;
      try {
        const response = await rechargeApi.confirmPayment(currentOrder.value.orderNo);
        if (response.success && response.data) {
          showToast(`充值成功！余额增加 ¥${currentOrder.value.amount}`, 'success');
          currentOrder.value = null;
          stopCountdown();
          await loadBalance();
        } else {
          showToast(response.message || '支付失败', 'error');
        }
      } catch (error) {
        showToast('支付失败', 'error');
      } finally {
        rechargeLoading.value = false;
      }
    };

    // 取消订单
    const cancelRechargeOrder = async () => {
      if (!currentOrder.value) return;
      
      try {
        const response = await rechargeApi.cancelOrder(currentOrder.value.orderNo);
        if (response.success) {
          showToast('订单已取消', 'info');
          currentOrder.value = null;
          stopCountdown();
        } else {
          showToast(response.message || '取消失败', 'error');
        }
      } catch (error) {
        showToast('取消失败', 'error');
      }
    };

    // 开始倒计时
    const startCountdown = (seconds) => {
      stopCountdown();
      remainingTime.value = seconds;
      countdownTimer.value = setInterval(() => {
        remainingTime.value--;
        if (remainingTime.value <= 0) {
          stopCountdown();
          currentOrder.value = null;
          showToast('订单已过期', 'warning');
        }
      }, 1000);
    };

    // 停止倒计时
    const stopCountdown = () => {
      if (countdownTimer.value) {
        clearInterval(countdownTimer.value);
        countdownTimer.value = null;
      }
    };

    // 格式化倒计时
    const formatCountdown = (seconds) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // 加载充值历史
    const loadRechargeHistory = async () => {
      try {
        const response = await rechargeApi.getOrders();
        if (response.success && response.data) {
          rechargeOrders.value = response.data;
        }
      } catch (error) {
        console.error('加载充值历史失败:', error);
      }
    };

    // 打开充值历史
    const openRechargeHistory = async () => {
      showRechargeHistory.value = true;
      await loadRechargeHistory();
    };

    // 检查过期订单通知
    const checkExpiredNotifications = async () => {
      if (!user.value) return;
      try {
        const response = await rechargeApi.getExpiredNotifications();
        if (response.success && response.data && response.data.length > 0) {
          for (const order of response.data) {
            showToast(`订单 ${order.orderNo} 已过期，充值金额 ¥${order.amount} 未到账`, 'warning');
          }
          // 如果当前订单过期了，清除它
          if (currentOrder.value && response.data.some(o => o.orderNo === currentOrder.value.orderNo)) {
            currentOrder.value = null;
            stopCountdown();
          }
        }
      } catch (error) {
        console.error('检查过期通知失败:', error);
      }
    };

    // 关闭充值弹窗
    const closeRecharge = () => {
      showRecharge.value = false;
      stopCountdown();
    };

    // 初始化
    onMounted(async () => {
      // 恢复用户信息
      const savedUser = localStorage.getItem('user');
      if (savedUser) {
        user.value = JSON.parse(savedUser);
        // 加载会话列表
        await loadSessions();
        // 加载用户余额
        await loadBalance();
        // 启动过期订单检查（每30秒）
        expiredCheckInterval.value = setInterval(checkExpiredNotifications, 30000);
      }
    });

    // 清理定时器
    onUnmounted(() => {
      stopCountdown();
      if (expiredCheckInterval.value) {
        clearInterval(expiredCheckInterval.value);
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
      // 会话
      sessions,
      currentSessionId,
      sessionsLoading,
      createNewSession,
      switchSession,
      deleteSessionConfirm,
      showSessionStats,
      showSessionStatsModal,
      sessionStatsLoading,
      sessionStatsData,
      // 模型列表
      showModelsModal,
      modelsLoading,
      modelsList,
      openModelsModal,
      // 聊天
      messages,
      inputMessage,
      isLoading,
      showSettings,
      showHistory,
      stats,
      messagesWrapper,
      inputField,
      fileInput,
      toast,
      chatHistory,
      historyLoading,
      enableWebSearch,  // 联网搜索开关
      deepThink,  // 深度思考开关(TOT)
      thoughtBranches,
      thoughtDepth,
      // 文件上传
      uploadedFile,
      isUploading,
      handleFileSelect,
      removeUploadedFile,
      formatFileSize,
      getInputPlaceholder,
      // 其他方法
      formatMessage,
      formatTime,
      formatDateTime,
      sendMessage,
      showStats,
      clearShortTermMemory,
      clearAllMemory,
      deleteAllHistory,
      openHistory,
      // 充值相关
      showRecharge,
      userBalance,
      rechargeAmount,
      customAmount,
      isCustomAmount,
      currentOrder,
      rechargeLoading,
      remainingTime,
      rechargeOrders,
      showRechargeHistory,
      openRecharge,
      closeRecharge,
      selectAmount,
      selectCustomAmount,
      getRechargeAmount,
      createRechargeOrder,
      confirmPayment,
      cancelRechargeOrder,
      formatCountdown,
      openRechargeHistory,
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
  gap: 0;
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.btn-sm {
  padding: 6px;
  min-width: auto;
}

.btn-sm svg {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: transparent;
}

.session-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.session-item.active {
  background: var(--primary-color);
  color: white;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.session-time {
  font-size: 12px;
  opacity: 0.7;
}

.session-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.session-stats-btn,
.session-delete {
  background: transparent;
  border: none;
  padding: 4px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
  color: inherit;
}

.session-stats-btn:hover,
.session-delete:hover {
  opacity: 1;
}

.session-stats-btn svg,
.session-delete svg {
  width: 16px;
  height: 16px;
}

.session-stats-btn:hover {
  color: var(--primary-color);
}

.session-delete:hover {
  color: #e74c3c;
}

.chat-container {
  flex: 1;
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

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}

.message-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
}

.message-cost {
  font-size: 11px;
  color: #ffd700;
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  cursor: help;
}

.message.assistant .message-meta {
  color: var(--text-muted);
}

.message.assistant .message-time {
  color: var(--text-muted);
}

.message.assistant .message-cost {
  color: #e67e22;
  background: rgba(230, 126, 34, 0.1);
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

/* 输入选项（联网搜索开关等） */
.input-options {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 10px;
  padding-left: 10px;
}

.toggle-switch {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  width: 36px;
  height: 20px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  position: relative;
  transition: background 0.3s;
  margin-right: 8px;
}

.toggle-slider::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background: #4CAF50;
}

.toggle-switch input:checked + .toggle-slider.deep-think-slider {
  background: #FF9800;
}

.toggle-switch input:checked + .toggle-slider::after {
  transform: translateX(16px);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 13px;
  font-weight: 500;
}

.toggle-label svg {
  opacity: 0.9;
}

.toggle-switch input:checked ~ .toggle-label {
  color: #4CAF50;
}

.toggle-switch input:checked + .toggle-slider.deep-think-slider ~ .toggle-label {
  color: #FF9800;
}

.toggle-switch input:checked ~ .toggle-label svg {
  stroke: #4CAF50;
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

/* 历史记录列表样式 */
.history-list {
  max-height: 60vh;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.history-item:last-child {
  border-bottom: none;
}

.history-user,
.history-assistant {
  margin-bottom: 8px;
  line-height: 1.5;
}

.history-label {
  font-weight: 600;
  color: var(--primary-color);
}

.history-assistant .history-label {
  color: var(--secondary-color);
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.history-time {
  font-size: 12px;
  color: var(--text-muted);
}

.history-cost {
  font-size: 12px;
  color: #e67e22;
  background: rgba(230, 126, 34, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  cursor: help;
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

/* 会话统计弹窗样式 */
.session-stats-content {
  padding: 10px 0;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-section:last-child {
  margin-bottom: 0;
}

.stats-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.stats-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-color);
}

.stats-value.model-name {
  color: var(--primary-color);
  font-size: 18px;
  background: rgba(52, 152, 219, 0.1);
  padding: 8px 16px;
  border-radius: 8px;
  display: inline-block;
}

.stats-value.cost-value {
  color: #e67e22;
  font-size: 32px;
}

.cost-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-box {
  background: var(--bg-color);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-box .stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.stat-box .stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-color);
}

/* 模型列表弹窗样式 */
.modal-models {
  max-width: 600px;
  max-height: 80vh;
}

.modal-models .modal-body {
  max-height: calc(80vh - 60px);
  overflow-y: auto;
}

.models-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.model-card {
  background: var(--bg-color);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.model-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.model-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.model-provider {
  font-size: 12px;
  color: var(--text-muted);
  background: var(--sidebar-bg);
  padding: 4px 8px;
  border-radius: 4px;
}

.model-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(230, 126, 34, 0.1);
  border-radius: 8px;
  margin-bottom: 12px;
}

.price-label {
  font-size: 13px;
  color: var(--text-muted);
}

.price-value {
  font-size: 16px;
  font-weight: 600;
  color: #e67e22;
}

.model-services {
  margin-bottom: 12px;
}

.service-count {
  font-size: 13px;
  color: var(--primary-color);
  background: rgba(52, 152, 219, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.model-description {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 12px;
}

.model-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  font-size: 12px;
  color: #27ae60;
  background: rgba(39, 174, 96, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
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
  .sidebar {
    display: none;
  }

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

/* 加载和空状态 */
.loading-text,
.empty-text {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
  font-size: 14px;
}

/* 文件上传样式 */
.uploaded-file-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--primary-light);
  border: 1px solid var(--primary);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 8px;
}

.uploaded-file-preview .file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary);
}

.uploaded-file-preview .file-name {
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.uploaded-file-preview .file-size {
  font-size: 12px;
  color: var(--text-muted);
}

.remove-file-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.remove-file-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.upload-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.upload-btn:hover:not(:disabled) {
  background: var(--primary-light);
  color: var(--primary);
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-btn svg {
  width: 20px;
  height: 20px;
}

.upload-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 用户余额显示 */
.user-balance {
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  color: #333;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 8px;
}

.user-balance:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

/* 充值弹窗 */
.modal-recharge {
  max-width: 420px;
}

.balance-display {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
}

.balance-label {
  display: block;
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.balance-value {
  font-size: 32px;
  font-weight: 700;
}

/* 待支付订单 */
.pending-order {
  background: #fff9e6;
  border: 1px solid #ffd700;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.pending-order h4 {
  color: #d97706;
  margin-bottom: 12px;
}

.order-no {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.order-amount {
  font-size: 16px;
  margin-bottom: 8px;
}

.order-amount strong {
  color: var(--primary);
  font-size: 24px;
}

.order-countdown {
  font-size: 14px;
  color: #059669;
}

.order-countdown.warning {
  color: #dc2626;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.order-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.order-actions .btn {
  flex: 1;
}

.payment-note {
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
}

/* 充值表单 */
.recharge-form h4 {
  margin-bottom: 12px;
  color: var(--text-color);
}

.amount-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}

.amount-btn {
  padding: 12px 8px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.amount-btn:hover {
  border-color: var(--primary);
  background: var(--primary-light);
}

.amount-btn.active {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

.custom-amount {
  margin-bottom: 16px;
}

.custom-amount label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-muted);
}

.custom-amount input {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
}

.custom-amount input:focus {
  border-color: var(--primary);
  outline: none;
}

.recharge-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-light);
  border-radius: 8px;
  margin-bottom: 16px;
}

.recharge-summary strong {
  font-size: 24px;
  color: var(--primary);
}

.btn-block {
  width: 100%;
}

.btn-lg {
  padding: 14px 24px;
  font-size: 16px;
}

.recharge-note {
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
}

.recharge-history-link {
  margin-top: 16px;
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.recharge-history-link a {
  color: var(--primary);
  text-decoration: none;
  font-size: 14px;
}

.recharge-history-link a:hover {
  text-decoration: underline;
}

/* 充值记录列表 */
.recharge-orders-list {
  max-height: 400px;
  overflow-y: auto;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.order-item:last-child {
  border-bottom: none;
}

.order-left {
  display: flex;
  flex-direction: column;
}

.order-amount-display {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
}

.order-time {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.order-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.order-status.paid {
  background: #d1fae5;
  color: #059669;
}

.order-status.pending {
  background: #fef3c7;
  color: #d97706;
}

.order-status.expired {
  background: #fee2e2;
  color: #dc2626;
}

.order-status.cancelled {
  background: #f3f4f6;
  color: #6b7280;
}
</style>
