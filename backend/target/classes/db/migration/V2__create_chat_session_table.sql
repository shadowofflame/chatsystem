-- 创建 chat_session 表
CREATE TABLE IF NOT EXISTS chat_session (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL DEFAULT '新对话',
    message_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 为现有的 chat_history 表中的会话创建对应的 chat_session 记录
INSERT INTO chat_session (user_id, session_id, title, message_count, created_at, updated_at)
SELECT 
    ch.user_id,
    ch.session_id,
    CONCAT('会话 ', SUBSTRING(ch.session_id, 1, 8)) as title,
    COUNT(*) as message_count,
    MIN(ch.created_at) as created_at,
    MAX(ch.created_at) as updated_at
FROM chat_history ch
WHERE ch.session_id NOT IN (SELECT session_id FROM chat_session)
GROUP BY ch.user_id, ch.session_id
ON DUPLICATE KEY UPDATE message_count = VALUES(message_count), updated_at = VALUES(updated_at);
