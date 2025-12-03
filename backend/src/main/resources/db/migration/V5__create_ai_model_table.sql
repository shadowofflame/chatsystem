-- V5: 创建AI模型表

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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_model_enabled (enabled),
    INDEX idx_model_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI模型配置表';

-- 插入初始模型数据
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
