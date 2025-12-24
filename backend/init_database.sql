-- ============================================
-- ChatSystem 数据库初始化脚本
-- 生成日期: 2025-12-07
-- 数据库类型: MySQL 8.0+
-- ============================================

-- 创建数据库（如果不存在）
-- CREATE DATABASE IF NOT EXISTS chatbot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE chatbot;

-- ============================================
-- 1. 用户表 (users)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    nickname VARCHAR(50) COMMENT '昵称',
    balance DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '账户余额',
    enabled BOOLEAN DEFAULT TRUE COMMENT '账户是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. 聊天历史表 (chat_history)
-- ============================================
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    session_id VARCHAR(100) COMMENT '会话ID',
    user_message TEXT NOT NULL COMMENT '用户消息',
    assistant_response TEXT COMMENT 'AI助手回复',
    input_char_count INT DEFAULT 0 COMMENT '输入字数',
    output_char_count INT DEFAULT 0 COMMENT '输出字数',
    total_char_count INT DEFAULT 0 COMMENT '总字数',
    cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '本次对话费用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天历史表';

-- ============================================
-- 3. 聊天会话表 (chat_session)
-- ============================================
CREATE TABLE IF NOT EXISTS chat_session (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    session_id VARCHAR(255) NOT NULL UNIQUE COMMENT '会话唯一标识',
    title VARCHAR(255) NOT NULL DEFAULT '新对话' COMMENT '会话标题',
    message_count INT NOT NULL DEFAULT 0 COMMENT '消息数量',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天会话表';

-- ============================================
-- 4. 充值订单表 (recharge_order)
-- ============================================
CREATE TABLE IF NOT EXISTS recharge_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(64) NOT NULL UNIQUE COMMENT '订单号',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    amount DECIMAL(10,2) NOT NULL COMMENT '充值金额',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '订单状态: PENDING-待支付, PAID-已支付, EXPIRED-已过期, CANCELLED-已取消',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    paid_at TIMESTAMP NULL COMMENT '支付时间',
    expired_at TIMESTAMP NULL COMMENT '过期时间',
    expire_time TIMESTAMP NOT NULL COMMENT '过期截止时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_order_no (order_no),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_expire_time (expire_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='充值订单表';

-- ============================================
-- 5. AI模型配置表 (ai_model)
-- ============================================
CREATE TABLE IF NOT EXISTS ai_model (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL UNIQUE COMMENT '模型名称',
    display_name VARCHAR(100) COMMENT '显示名称',
    price_per_10k_chars DECIMAL(10, 4) NOT NULL DEFAULT 1.0000 COMMENT '每10000字收费（元）',
    service_count BIGINT DEFAULT 0 COMMENT '服务数量',
    service_description TEXT COMMENT '服务描述',
    capabilities VARCHAR(500) COMMENT '能力标签（逗号分隔）',
    provider VARCHAR(50) COMMENT '模型提供商',
    max_context_length INT COMMENT '最大上下文长度',
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    sort_order INT DEFAULT 100 COMMENT '排序权重',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_model_enabled (enabled),
    INDEX idx_model_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI模型配置表';

-- ============================================
-- 6. 初始化AI模型数据
-- ============================================
INSERT INTO ai_model (model_name, display_name, price_per_10k_chars, service_count, service_description, capabilities, provider, max_context_length, enabled, sort_order) VALUES
('deepseek-chat', 'DeepSeek Chat', 1.0000, 0, 
 'DeepSeek Chat 是一款强大的通用对话模型，支持多轮对话、代码生成、文本创作等多种任务。具有出色的中英文理解能力，响应速度快，性价比高。',
 '智能对话,代码生成,文本创作,知识问答,翻译',
 'DeepSeek', 32768, TRUE, 1),

('deepseek-coder', 'DeepSeek Coder', 1.5000, 0,
 'DeepSeek Coder 是专门针对编程任务优化的模型，擅长代码生成、代码解释、Bug修复、代码重构等任务。支持多种编程语言。',
 '代码生成,代码解释,Bug修复,代码重构,技术文档',
 'DeepSeek', 16384, TRUE, 2),

('gpt-4o', 'GPT-4o', 5.0000, 0,
 'OpenAI最新的多模态模型，具有卓越的推理能力和创造力。支持文本、图像输入，适合复杂任务和高质量内容生成。',
 '智能对话,图像理解,高级推理,创意写作,数据分析',
 'OpenAI', 128000, TRUE, 3),

('gpt-4o-mini', 'GPT-4o Mini', 2.0000, 0,
 'GPT-4o的轻量版本，在保持高质量输出的同时提供更快的响应速度和更低的成本，适合日常对话和一般任务。',
 '智能对话,文本生成,知识问答,翻译',
 'OpenAI', 128000, TRUE, 4),

('claude-3-5-sonnet', 'Claude 3.5 Sonnet', 4.0000, 0,
 'Anthropic的Claude 3.5 Sonnet模型，在创意写作、分析推理方面表现出色。具有良好的安全性和可靠性。',
 '智能对话,创意写作,分析推理,代码生成,研究辅助',
 'Anthropic', 200000, TRUE, 5),

('qwen-max', 'Qwen Max', 2.5000, 0,
 '阿里云通义千问旗舰模型，具有强大的中文理解和生成能力，支持长文本处理，适合各种复杂任务。',
 '智能对话,文本生成,知识问答,代码生成,翻译',
 'Alibaba', 32000, TRUE, 6),

('glm-4', 'GLM-4', 1.5000, 0,
 '智谱AI的GLM-4模型，中文理解能力强，支持多轮对话和复杂推理，性价比高。',
 '智能对话,文本生成,知识问答,代码辅助',
 'Zhipu', 128000, TRUE, 7);

-- ============================================
-- 完成提示
-- ============================================
SELECT '数据库初始化完成！' AS message;
SELECT '已创建的表:' AS info;
SELECT 'users - 用户表' AS table_name
UNION SELECT 'chat_history - 聊天历史表'
UNION SELECT 'chat_session - 聊天会话表'
UNION SELECT 'recharge_order - 充值订单表'
UNION SELECT 'ai_model - AI模型配置表';
