package com.chatbot.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionStatsDTO {
    
    // 使用的模型
    private String model;
    
    // 输入字数
    private Integer inputCharCount;
    
    // 输出字数
    private Integer outputCharCount;
    
    // 总字数
    private Integer totalCharCount;
    
    // 对话次数
    private Integer messageCount;
    
    // 总消费金额
    private BigDecimal totalCost;
}
