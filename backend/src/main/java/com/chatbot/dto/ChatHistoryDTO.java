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
public class ChatHistoryDTO {
    
    private Long id;
    private String sessionId;
    private String userMessage;
    private String assistantResponse;
    private LocalDateTime createdAt;
    
    // 字数统计
    private Integer inputCharCount;
    private Integer outputCharCount;
    private Integer totalCharCount;
    
    // 费用（精确到小数点后两位）
    private BigDecimal cost;
}
