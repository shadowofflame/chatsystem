-- V4: 为 chat_history 表添加字数统计和费用字段

-- 使用 MySQL 存储过程来安全添加列
DELIMITER //

DROP PROCEDURE IF EXISTS add_column_if_not_exists //

CREATE PROCEDURE add_column_if_not_exists()
BEGIN
    -- 添加 input_char_count 字段
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                   WHERE TABLE_SCHEMA = DATABASE() 
                   AND TABLE_NAME = 'chat_history' 
                   AND COLUMN_NAME = 'input_char_count') THEN
        ALTER TABLE chat_history ADD COLUMN input_char_count INT DEFAULT 0;
    END IF;

    -- 添加 output_char_count 字段
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                   WHERE TABLE_SCHEMA = DATABASE() 
                   AND TABLE_NAME = 'chat_history' 
                   AND COLUMN_NAME = 'output_char_count') THEN
        ALTER TABLE chat_history ADD COLUMN output_char_count INT DEFAULT 0;
    END IF;

    -- 添加 total_char_count 字段
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                   WHERE TABLE_SCHEMA = DATABASE() 
                   AND TABLE_NAME = 'chat_history' 
                   AND COLUMN_NAME = 'total_char_count') THEN
        ALTER TABLE chat_history ADD COLUMN total_char_count INT DEFAULT 0;
    END IF;

    -- 添加 cost 字段
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                   WHERE TABLE_SCHEMA = DATABASE() 
                   AND TABLE_NAME = 'chat_history' 
                   AND COLUMN_NAME = 'cost') THEN
        ALTER TABLE chat_history ADD COLUMN cost DECIMAL(10, 2) DEFAULT 0.00;
    END IF;
END //

DELIMITER ;

-- 执行存储过程
CALL add_column_if_not_exists();

-- 删除存储过程
DROP PROCEDURE IF EXISTS add_column_if_not_exists;

-- 为现有记录计算字数和费用
UPDATE chat_history 
SET 
    input_char_count = CHAR_LENGTH(COALESCE(user_message, '')),
    output_char_count = CHAR_LENGTH(COALESCE(assistant_response, '')),
    total_char_count = CHAR_LENGTH(COALESCE(user_message, '')) + CHAR_LENGTH(COALESCE(assistant_response, '')),
    cost = ROUND((CHAR_LENGTH(COALESCE(user_message, '')) + CHAR_LENGTH(COALESCE(assistant_response, ''))) / 10000.0, 2)
WHERE input_char_count = 0 OR input_char_count IS NULL;
