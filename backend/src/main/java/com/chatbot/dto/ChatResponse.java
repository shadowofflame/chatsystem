package com.chatbot.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {
    
    private String message;
    private String sessionId;
    private LocalDateTime timestamp;
    private boolean success;
    private String error;
    
    // TOT 深度思考相关字段
    private String thinkingProcess;     // 思考过程
    private Double totScore;            // TOT 最佳得分
    private Boolean deepThink;          // 是否使用了深度思考
    
    // 费用相关字段
    private Integer inputCharCount;     // 输入字数
    private Integer outputCharCount;    // 输出字数
    private Integer totalCharCount;     // 总字数
    private BigDecimal cost;            // 本次对话费用
    private BigDecimal newBalance;      // 扣费后的新余额
    
    public static ChatResponse success(String message, String sessionId) {
        return ChatResponse.builder()
                .message(message)
                .sessionId(sessionId)
                .timestamp(LocalDateTime.now())
                .success(true)
                .build();
    }
    
    public static ChatResponse successWithThinking(String message, String sessionId, 
            String thinkingProcess, Double totScore, Boolean deepThink) {
        return ChatResponse.builder()
                .message(message)
                .sessionId(sessionId)
                .timestamp(LocalDateTime.now())
                .success(true)
                .thinkingProcess(thinkingProcess)
                .totScore(totScore)
                .deepThink(deepThink)
                .build();
    }
    
    public static ChatResponse error(String error) {
        return ChatResponse.builder()
                .error(error)
                .timestamp(LocalDateTime.now())
                .success(false)
                .build();
    }
}
